"""Unit tests for the recommendation engine. Run:  cd backend && python -m unittest discover -s tests -v"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import recommendation_engine as engine  # noqa: E402

BOOKS = [
    {"bookId": "B1", "title": "Java Basics", "author": "A", "category": "Programming", "subject": "Java",
     "keywords": "java, oop, classes", "description": "Learn Java object oriented programming.", "imageUrl": ""},
    {"bookId": "B2", "title": "Java Projects", "author": "B", "category": "Programming", "subject": "Java",
     "keywords": "java, projects", "description": "Build Java projects step by step.", "imageUrl": ""},
    {"bookId": "B3", "title": "Machine Learning Basics", "author": "C", "category": "Artificial Intelligence",
     "subject": "Machine Learning", "keywords": "machine learning, regression",
     "description": "Regression and classification explained.", "imageUrl": ""},
    {"bookId": "B4", "title": "Cyber Security Basics", "author": "D", "category": "Cyber Security",
     "subject": "Cyber Security", "keywords": "encryption, firewall",
     "description": "Encryption and network defence.", "imageUrl": ""},
    {"bookId": "B5", "title": "SQL Guide", "author": "E", "category": "Databases", "subject": "SQL",
     "keywords": "sql, joins", "description": "Queries and joins for databases.", "imageUrl": ""},
    {"bookId": "B6", "title": "Python Basics", "author": "F", "category": "Programming", "subject": "Python",
     "keywords": "python, functions", "description": "Python programming for beginners.", "imageUrl": ""},
]


class TokenizeTests(unittest.TestCase):
    def test_lowercase_and_stopwords(self):
        self.assertEqual(engine.tokenize("The Java and the JVM"), ["java", "jvm"])

    def test_short_forms_are_expanded(self):
        tokens = engine.tokenize("AI")
        self.assertIn("ai", tokens)
        self.assertIn("artificial", tokens)

    def test_empty_text(self):
        self.assertEqual(engine.tokenize(""), [])
        self.assertEqual(engine.tokenize(None), [])


class MathTests(unittest.TestCase):
    def test_cosine_identical_vectors_is_one(self):
        v = engine._normalize({"a": 1.0, "b": 2.0})
        self.assertAlmostEqual(engine.cosine_similarity(v, v), 1.0)

    def test_cosine_no_common_words_is_zero(self):
        self.assertEqual(engine.cosine_similarity({"a": 1.0}, {"b": 1.0}), 0.0)

    def test_rare_words_get_higher_idf(self):
        idf = engine.compute_idf([engine.term_counts([("java common", 1)]),
                                  engine.term_counts([("python common", 1)])])
        self.assertGreater(idf["java"], idf["common"])


class RecommendTests(unittest.TestCase):
    def test_java_interest_returns_java_books_first(self):
        result = engine.recommend(BOOKS, ["Java"], [])
        self.assertEqual({r["bookId"] for r in result[:2]}, {"B1", "B2"})

    def test_multiple_interests(self):
        result = engine.recommend(BOOKS, ["Java", "Machine Learning"], [])
        ids = [r["bookId"] for r in result]
        self.assertIn("B1", ids)
        self.assertIn("B3", ids)

    def test_scores_are_sorted_and_between_0_and_1(self):
        result = engine.recommend(BOOKS, ["Java", "programming"], ["Programming"])
        scores = [r["score"] for r in result]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertTrue(all(0 < s <= 1 for s in scores))

    def test_top_n_limit(self):
        self.assertLessEqual(len(engine.recommend(BOOKS, ["programming"], [], top_n=2)), 2)

    def test_no_matching_books(self):
        self.assertEqual(engine.recommend(BOOKS, ["zzzz qqqq"], []), [])

    def test_empty_book_list(self):
        self.assertEqual(engine.recommend([], ["Java"], []), [])

    def test_new_student_without_history_still_gets_results(self):
        self.assertTrue(engine.recommend(BOOKS, ["SQL"], [], history=[]))

    def test_read_books_are_not_recommended_again(self):
        result = engine.recommend(BOOKS, ["Java"], [], history=[{"bookId": "B1", "rating": 5}])
        self.assertNotIn("B1", [r["bookId"] for r in result])

    def test_history_changes_the_results(self):
        # "basics" alone does not match the book "Java Projects" (B2).
        # A student who already read "Java Basics" (B1) should now get B2 through history.
        without = engine.recommend(BOOKS, ["basics"], [])
        with_hist = engine.recommend(BOOKS, ["basics"], [], history=[{"bookId": "B1", "rating": 5}])
        self.assertNotIn("B2", [r["bookId"] for r in without])
        self.assertIn("B2", [r["bookId"] for r in with_hist])

    def test_only_history_no_interests(self):
        result = engine.recommend(BOOKS, [], [], history=[{"bookId": "B1", "rating": 5}])
        self.assertEqual(result[0]["bookId"], "B2")

    def test_low_rated_book_is_ignored_for_profile(self):
        result = engine.recommend(BOOKS, [], [], history=[{"bookId": "B1", "rating": 1}])
        self.assertEqual(result, [])

    def test_result_has_expected_fields(self):
        item = engine.recommend(BOOKS, ["Java"], [])[0]
        for key in ("bookId", "title", "author", "category", "subject", "score", "matchPercent", "matchedTerms"):
            self.assertIn(key, item)


if __name__ == "__main__":
    unittest.main()
