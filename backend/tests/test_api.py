"""
API tests for lambda_function.py. DynamoDB is replaced by mocks, so no AWS is needed.
Run:  cd backend && python -m unittest discover -s tests -v
"""
import json
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lambda_function as lf  # noqa: E402
from errors import ServiceUnavailableError  # noqa: E402

BOOKS = [
    {"bookId": "B1", "title": "Java Basics", "author": "A", "category": "Programming", "subject": "Java",
     "keywords": "java, oop", "description": "Learn Java programming.", "imageUrl": "images/B1.svg"},
    {"bookId": "B2", "title": "Machine Learning Basics", "author": "B", "category": "Artificial Intelligence",
     "subject": "Machine Learning", "keywords": "machine learning", "description": "Regression models.", "imageUrl": ""},
    {"bookId": "B3", "title": "Java Projects", "author": "C", "category": "Programming", "subject": "Java",
     "keywords": "java, projects", "description": "Java projects for practice.", "imageUrl": ""},
]


def call(method, path, body=None, query=None):
    event = {"httpMethod": method, "path": path, "queryStringParameters": query,
             "body": json.dumps(body) if body is not None else None}
    result = lf.lambda_handler(event, None)
    return result["statusCode"], json.loads(result["body"]), result["headers"]


@mock.patch("lambda_function.db")
class ApiTests(unittest.TestCase):
    def setup_db(self, db, student=None, history=None, books=BOOKS):
        db.get_student.return_value = student
        db.get_history.return_value = history or []
        db.get_all_books.return_value = books
        db.get_book.side_effect = lambda bid: next((b for b in BOOKS if b["bookId"] == bid), None)

    # 1. valid student
    def test_01_valid_student_gets_recommendations(self, db):
        self.setup_db(db)
        status, body, headers = call("POST", "/recommendations",
                                     {"studentId": "ST001", "interests": ["Java"], "subjects": []})
        self.assertEqual(status, 200)
        self.assertEqual(body["recommendations"][0]["subject"], "Java")
        self.assertIn("Access-Control-Allow-Origin", headers)      # CORS

    # 2. invalid student
    def test_02_invalid_student_id(self, db):
        self.setup_db(db)
        status, body, _ = call("POST", "/recommendations", {"studentId": "bad id!!", "interests": ["Java"]})
        self.assertEqual(status, 400)
        self.assertIn("studentId", body["error"])

    def test_02b_missing_student_id(self, db):
        self.setup_db(db)
        status, _, _ = call("POST", "/recommendations", {"interests": ["Java"]})
        self.assertEqual(status, 400)

    # 3. empty interests
    def test_03_empty_interests_and_no_history(self, db):
        self.setup_db(db)
        status, body, _ = call("POST", "/recommendations", {"studentId": "ST001", "interests": [], "subjects": []})
        self.assertEqual(status, 400)
        self.assertIn("interest", body["error"])

    # 4. multiple interests
    def test_04_multiple_interests(self, db):
        self.setup_db(db)
        _, body, _ = call("POST", "/recommendations", {"studentId": "ST001", "interests": ["Java", "Machine Learning"]})
        ids = [r["bookId"] for r in body["recommendations"]]
        self.assertIn("B1", ids)
        self.assertIn("B2", ids)

    # 5. new student, no history
    def test_05_new_student_no_history(self, db):
        self.setup_db(db)
        status, body, _ = call("POST", "/recommendations", {"studentId": "NEW9", "interests": ["Java"]})
        self.assertEqual(status, 200)
        self.assertEqual(body["historyCount"], 0)
        self.assertTrue(body["recommendations"])

    # 6. existing student with history (read book is not repeated)
    def test_06_student_with_history(self, db):
        self.setup_db(db, history=[{"historyId": "H1", "studentId": "ST001", "bookId": "B1", "rating": 5}])
        _, body, _ = call("POST", "/recommendations", {"studentId": "ST001", "interests": ["Java"]})
        ids = [r["bookId"] for r in body["recommendations"]]
        self.assertEqual(body["historyCount"], 1)
        self.assertNotIn("B1", ids)
        self.assertIn("B3", ids)

    # 7. no matching books
    def test_07_no_matching_books(self, db):
        self.setup_db(db)
        status, body, _ = call("POST", "/recommendations", {"studentId": "ST001", "interests": ["xyzabc"]})
        self.assertEqual(status, 200)
        self.assertEqual(body["recommendations"], [])
        self.assertIn("message", body)

    def test_07b_no_books_in_database(self, db):
        self.setup_db(db, books=[])
        status, body, _ = call("POST", "/recommendations", {"studentId": "ST001", "interests": ["Java"]})
        self.assertEqual(status, 200)
        self.assertEqual(body["recommendations"], [])

    # 8. book selection
    def test_08_book_selection_saved(self, db):
        self.setup_db(db)
        db.add_history.return_value = {"historyId": "H1", "studentId": "ST001", "bookId": "B1", "selectedAt": "2026-01-01T00:00:00Z"}
        status, body, _ = call("POST", "/history", {"studentId": "ST001", "bookId": "B1", "rating": 5})
        self.assertEqual(status, 201)
        db.add_history.assert_called_once_with("ST001", "B1", 5)

    def test_08b_selecting_unknown_book(self, db):
        self.setup_db(db)
        status, _, _ = call("POST", "/history", {"studentId": "ST001", "bookId": "B999"})
        self.assertEqual(status, 404)

    def test_08c_invalid_rating(self, db):
        self.setup_db(db)
        status, _, _ = call("POST", "/history", {"studentId": "ST001", "bookId": "B1", "rating": 9})
        self.assertEqual(status, 400)

    # 9. reading history
    def test_09_reading_history(self, db):
        self.setup_db(db, history=[{"historyId": "H1", "studentId": "ST001", "bookId": "B1", "selectedAt": "2026-01-01T00:00:00Z"}])
        status, body, _ = call("GET", "/history/ST001")
        self.assertEqual(status, 200)
        self.assertEqual(body["count"], 1)
        self.assertEqual(body["history"][0]["title"], "Java Basics")

    def test_09b_empty_history(self, db):
        self.setup_db(db)
        status, body, _ = call("GET", "/history/NEW9")
        self.assertEqual((status, body["count"]), (200, 0))

    # 10. API failure (unknown route / wrong method)
    def test_10_unknown_route(self, db):
        status, body, _ = call("GET", "/nothing")
        self.assertEqual(status, 404)

    def test_10b_wrong_method(self, db):
        status, _, _ = call("GET", "/recommendations")
        self.assertEqual(status, 405)

    # 11. DynamoDB failure
    def test_11_dynamodb_failure(self, db):
        db.get_student.side_effect = ServiceUnavailableError("The database is temporarily unavailable.")
        status, body, _ = call("POST", "/recommendations", {"studentId": "ST001", "interests": ["Java"]})
        self.assertEqual(status, 503)
        self.assertIn("temporarily unavailable", body["error"])

    def test_11b_unexpected_crash_returns_500(self, db):
        db.get_student.side_effect = RuntimeError("boom")
        status, body, _ = call("POST", "/recommendations", {"studentId": "ST001", "interests": ["Java"]})
        self.assertEqual(status, 500)
        self.assertIn("error", body)

    # 12. invalid API request
    def test_12_invalid_json_body(self, db):
        result = lf.lambda_handler({"httpMethod": "POST", "path": "/recommendations", "body": "{not json"}, None)
        self.assertEqual(result["statusCode"], 400)

    def test_12b_missing_body(self, db):
        status, _, _ = call("POST", "/recommendations")
        self.assertEqual(status, 400)

    def test_12c_interests_wrong_type(self, db):
        self.setup_db(db)
        status, _, _ = call("POST", "/recommendations", {"studentId": "ST001", "interests": 123})
        self.assertEqual(status, 400)

    # extra: other endpoints
    def test_health(self, db):
        self.assertEqual(call("GET", "/health")[0], 200)

    def test_options_preflight(self, db):
        self.assertEqual(call("OPTIONS", "/recommendations")[0], 200)

    def test_get_book_and_not_found(self, db):
        self.setup_db(db)
        self.assertEqual(call("GET", "/books/B1")[0], 200)
        self.assertEqual(call("GET", "/books/B999")[0], 404)

    def test_list_books_with_search(self, db):
        self.setup_db(db)
        _, body, _ = call("GET", "/books", query={"q": "machine"})
        self.assertEqual(body["count"], 1)

    def test_create_student(self, db):
        self.setup_db(db)
        status, body, _ = call("POST", "/students", {"studentId": "ST050", "name": "Test", "interests": "Java, AI"})
        self.assertEqual(status, 201)
        self.assertEqual(body["interests"], ["Java", "AI"])

    def test_create_student_missing_name(self, db):
        self.setup_db(db)
        self.assertEqual(call("POST", "/students", {"studentId": "ST050"})[0], 400)

    def test_get_student_not_found(self, db):
        self.setup_db(db)
        self.assertEqual(call("GET", "/students/ST404")[0], 404)


if __name__ == "__main__":
    unittest.main()
