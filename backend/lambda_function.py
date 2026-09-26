"""
lambda_function.py - The AWS Lambda entry point (the "controller").

API Gateway sends every HTTP request here. We:
  1. read the method + path      (e.g. POST /recommendations)
  2. validate the input
  3. call dynamodb_service / recommendation_engine
  4. return a JSON response with the right HTTP status and CORS headers

Handler name to use in AWS Lambda:  lambda_function.lambda_handler
"""
import base64
import json
import logging
import re

import config
import dynamodb_service as db
import recommendation_engine as engine
from errors import NotFoundError, ServiceUnavailableError, ValidationError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
}

STUDENT_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,20}$")
BOOK_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,20}$")


# ============================================================ helpers
def response(status, body):
    """Build the response format API Gateway expects."""
    return {"statusCode": status, "headers": CORS_HEADERS, "body": json.dumps(body)}


def get_method_and_path(event):
    """Works for API Gateway HTTP API (v2) and REST API (v1) events."""
    http = (event.get("requestContext") or {}).get("http") or {}
    method = http.get("method") or event.get("httpMethod") or ""
    path = event.get("rawPath") or event.get("path") or "/"
    return method.upper(), "/" + path.strip("/")


def parse_body(event):
    """Read the JSON body. Raises ValidationError if it is missing or broken."""
    raw = event.get("body")
    if raw is None or raw == "":
        raise ValidationError("Request body is required (JSON).")
    if event.get("isBase64Encoded"):
        raw = base64.b64decode(raw).decode("utf-8")
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        raise ValidationError("Request body must be valid JSON.")
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object.")
    return data


def validate_student_id(value):
    if value is None or str(value).strip() == "":
        raise ValidationError("studentId is required.")
    value = str(value).strip()
    if not STUDENT_ID_RE.match(value):
        raise ValidationError("studentId may contain only letters, numbers, - and _ (max 20 characters).")
    return value


def clean_list(value, field):
    """Accept a list (or comma separated text) and return a clean list of short strings."""
    if value is None:
        return []
    if isinstance(value, str):
        value = value.split(",")
    if not isinstance(value, list):
        raise ValidationError(f"{field} must be a list of text values.")
    result = []
    for item in value:
        if not isinstance(item, str):
            raise ValidationError(f"{field} must contain only text values.")
        item = item.strip()
        if item and item.lower() not in [r.lower() for r in result]:
            result.append(item[:50])
    if len(result) > 30:
        raise ValidationError(f"{field} can contain at most 30 items.")
    return result


def public_book(book, with_rank_fields=False):
    fields = ["bookId", "title", "author", "category", "subject", "keywords", "description", "imageUrl"]
    if with_rank_fields:
        fields += ["score", "matchPercent", "matchedTerms"]
    return {k: book.get(k) for k in fields if k in book}


# ============================================================ route handlers
def health(event):
    return response(200, {"status": "ok", "service": "AI Library Book Recommendation API"})


def list_books(event):
    params = event.get("queryStringParameters") or {}
    books = db.get_all_books()
    q = (params.get("q") or "").strip().lower()
    category = (params.get("category") or "").strip().lower()
    if category:
        books = [b for b in books if b.get("category", "").lower() == category]
    if q:
        books = [b for b in books if q in " ".join(
            [b.get("title", ""), b.get("author", ""), b.get("subject", ""), b.get("keywords", "")]).lower()]
    books = sorted(books, key=lambda b: b.get("bookId", ""))
    return response(200, {"count": len(books), "books": [public_book(b) for b in books]})


def get_book(event, book_id):
    if not BOOK_ID_RE.match(book_id):
        raise ValidationError("Invalid bookId.")
    book = db.get_book(book_id)
    if not book:
        raise NotFoundError(f"Book {book_id} was not found.")
    return response(200, public_book(book))


def create_student(event):
    data = parse_body(event)
    student_id = validate_student_id(data.get("studentId"))
    name = str(data.get("name") or "").strip()
    if not name:
        raise ValidationError("name is required.")
    student = {
        "studentId": student_id,
        "name": name[:80],
        "department": str(data.get("department") or "").strip()[:60],
        "year": str(data.get("year") or "").strip()[:20],
        "interests": clean_list(data.get("interests"), "interests"),
        "subjects": clean_list(data.get("subjects"), "subjects"),
    }
    existed = db.get_student(student_id) is not None
    db.save_student(student)
    logger.info("Student saved: %s", student_id)
    return response(200 if existed else 201, student)


def get_student(event, student_id):
    student_id = validate_student_id(student_id)
    student = db.get_student(student_id)
    if not student:
        raise NotFoundError(f"Student {student_id} was not found.")
    return response(200, student)


def recommendations(event):
    data = parse_body(event)
    student_id = validate_student_id(data.get("studentId"))
    interests = clean_list(data.get("interests"), "interests")
    subjects = clean_list(data.get("subjects"), "subjects")

    student = db.get_student(student_id)
    if student and not interests and not subjects:       # use saved profile if request is empty
        interests = student.get("interests", [])
        subjects = student.get("subjects", [])

    history = db.get_history(student_id)
    history_input = [{"bookId": h.get("bookId"), "rating": h.get("rating")} for h in history]

    if not interests and not subjects and not history:
        raise ValidationError("Please select at least one interest or subject.")

    books = db.get_all_books()
    if not books:
        return response(200, {"studentId": student_id, "recommendations": [],
                              "message": "The library has no books yet. Please add books and try again."})

    results = engine.recommend(books, interests, subjects, history_input, top_n=config.TOP_N)
    body = {
        "studentId": student_id,
        "interests": interests,
        "subjects": subjects,
        "historyCount": len(history),
        "recommendations": [public_book(r, with_rank_fields=True) for r in results],
    }
    if not results:
        body["message"] = "No matching books were found. Try different interests or subjects."
    logger.info("Recommendations for %s: %d results (history=%d)", student_id, len(results), len(history))
    return response(200, body)


def add_history(event):
    data = parse_body(event)
    student_id = validate_student_id(data.get("studentId"))
    book_id = str(data.get("bookId") or "").strip()
    if not book_id or not BOOK_ID_RE.match(book_id):
        raise ValidationError("A valid bookId is required.")
    rating = data.get("rating")
    if rating is not None:
        if isinstance(rating, bool) or not isinstance(rating, int) or not 1 <= rating <= 5:
            raise ValidationError("rating must be a whole number from 1 to 5.")
    if not db.get_book(book_id):
        raise NotFoundError(f"Book {book_id} was not found.")
    item = db.add_history(student_id, book_id, rating)
    logger.info("History saved: %s -> %s", student_id, book_id)
    return response(201, item)


def get_history(event, student_id):
    student_id = validate_student_id(student_id)
    history = db.get_history(student_id)
    result = []
    for h in history:
        book = db.get_book(h.get("bookId")) or {}
        entry = dict(h)
        entry.update({k: book.get(k) for k in ("title", "author", "category", "subject", "imageUrl")})
        result.append(entry)
    return response(200, {"studentId": student_id, "count": len(result), "history": result})


# ============================================================ router
ROUTES = [
    ("GET", re.compile(r"^/health$"), lambda e, m: health(e)),
    ("GET", re.compile(r"^/books$"), lambda e, m: list_books(e)),
    ("GET", re.compile(r"^/books/([^/]+)$"), lambda e, m: get_book(e, m.group(1))),
    ("POST", re.compile(r"^/students$"), lambda e, m: create_student(e)),
    ("GET", re.compile(r"^/students/([^/]+)$"), lambda e, m: get_student(e, m.group(1))),
    ("POST", re.compile(r"^/recommendations$"), lambda e, m: recommendations(e)),
    ("POST", re.compile(r"^/history$"), lambda e, m: add_history(e)),
    ("GET", re.compile(r"^/history/([^/]+)$"), lambda e, m: get_history(e, m.group(1))),
]


def lambda_handler(event, context):
    """Main function called by AWS Lambda."""
    try:
        method, path = get_method_and_path(event)
        logger.info("Request: %s %s", method, path)

        if method == "OPTIONS":                      # browser CORS pre-flight check
            return response(200, {})

        path_found = False
        for route_method, pattern, handler in ROUTES:
            match = pattern.match(path)
            if match:
                path_found = True
                if route_method == method:
                    return handler(event, match)
        if path_found:
            return response(405, {"error": f"Method {method} is not allowed for {path}."})
        return response(404, {"error": f"Route {method} {path} does not exist."})

    except ValidationError as exc:
        logger.warning("Validation error: %s", exc)
        return response(400, {"error": str(exc)})
    except NotFoundError as exc:
        return response(404, {"error": str(exc)})
    except ServiceUnavailableError as exc:
        return response(503, {"error": str(exc)})
    except Exception:                                # last safety net: never crash
        logger.exception("Unexpected error")
        return response(500, {"error": "Something went wrong on the server. Please try again."})
