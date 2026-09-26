"""
dynamodb_service.py - Everything that talks to Amazon DynamoDB (through Boto3).

Tables: Students, Books, ReadingHistory (names come from config.py).
If USE_LOCAL_STORAGE=true the functions use local_store.py instead (no AWS needed).
"""
import logging
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import config
import local_store
import s3_service
from errors import ServiceUnavailableError

logger = logging.getLogger()

try:
    import boto3
    from boto3.dynamodb.conditions import Key
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:  # pragma: no cover  (lets unit tests run without boto3)
    boto3 = None
    Key = None

    class ClientError(Exception):
        pass

    class BotoCoreError(Exception):
        pass

_dynamodb = None
_books_cache = {"items": None, "time": 0.0}


def _db():
    """Create the DynamoDB resource once and reuse it."""
    global _dynamodb
    if boto3 is None:
        raise ServiceUnavailableError("boto3 is not installed.")
    if _dynamodb is None:
        _dynamodb = boto3.resource("dynamodb", region_name=config.AWS_REGION)
    return _dynamodb


def _clean(value):
    """DynamoDB returns numbers as Decimal. Convert to int/float so JSON works."""
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    if isinstance(value, list):
        return [_clean(v) for v in value]
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items()}
    return value


def _fail(action, exc):
    logger.error("DynamoDB error while %s: %s", action, exc)
    raise ServiceUnavailableError("The database is temporarily unavailable. Please try again in a moment.")


# ------------------------------------------------------------------ Books
def get_all_books(force_refresh=False):
    """Return all books. Cached for a few minutes so warm Lambdas are fast."""
    if config.USE_LOCAL_STORAGE:
        return local_store.get_all_books()

    now = time.time()
    if (not force_refresh and _books_cache["items"] is not None
            and now - _books_cache["time"] < config.BOOKS_CACHE_SECONDS):
        return _books_cache["items"]

    try:
        table = _db().Table(config.BOOKS_TABLE)
        response = table.scan()
        items = response.get("Items", [])
        while "LastEvaluatedKey" in response:          # scan is paginated (1 MB per page)
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))
    except (ClientError, BotoCoreError) as exc:
        _fail("reading books", exc)

    books = [_clean(i) for i in items]
    if not books:                                       # table empty -> try the S3 CSV file
        logger.warning("Books table is empty. Trying S3 dataset/books.csv")
        try:
            books = s3_service.load_books_from_s3()
        except ServiceUnavailableError:
            books = []
    _books_cache["items"], _books_cache["time"] = books, now
    return books


def get_book(book_id):
    """Return one book or None."""
    if config.USE_LOCAL_STORAGE:
        return local_store.get_book(book_id)
    try:
        item = _db().Table(config.BOOKS_TABLE).get_item(Key={"bookId": book_id}).get("Item")
    except (ClientError, BotoCoreError) as exc:
        _fail("reading a book", exc)
    return _clean(item) if item else None


# --------------------------------------------------------------- Students
def get_student(student_id):
    if config.USE_LOCAL_STORAGE:
        return local_store.get_student(student_id)
    try:
        item = _db().Table(config.STUDENTS_TABLE).get_item(Key={"studentId": student_id}).get("Item")
    except (ClientError, BotoCoreError) as exc:
        _fail("reading a student", exc)
    return _clean(item) if item else None


def save_student(student):
    """Create or update a student."""
    if config.USE_LOCAL_STORAGE:
        return local_store.save_student(student)
    try:
        _db().Table(config.STUDENTS_TABLE).put_item(Item=student)
    except (ClientError, BotoCoreError) as exc:
        _fail("saving a student", exc)
    return student


# ---------------------------------------------------------------- History
def add_history(student_id, book_id, rating=None):
    """Store 'student selected this book'."""
    if config.USE_LOCAL_STORAGE:
        return local_store.add_history(student_id, book_id, rating)
    item = {
        "historyId": "H" + uuid.uuid4().hex[:12],
        "studentId": student_id,
        "bookId": book_id,
        "selectedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }
    if rating is not None:
        item["rating"] = rating
    try:
        _db().Table(config.HISTORY_TABLE).put_item(Item=item)
    except (ClientError, BotoCoreError) as exc:
        _fail("saving reading history", exc)
    return item


def get_history(student_id):
    """All books a student selected, newest first (uses the studentId-index)."""
    if config.USE_LOCAL_STORAGE:
        return local_store.get_history(student_id)
    try:
        table = _db().Table(config.HISTORY_TABLE)
        kwargs = {
            "IndexName": config.HISTORY_INDEX,
            "KeyConditionExpression": Key("studentId").eq(student_id),
            "ScanIndexForward": False,      # newest first
        }
        response = table.query(**kwargs)
        items = response.get("Items", [])
        while "LastEvaluatedKey" in response:
            response = table.query(ExclusiveStartKey=response["LastEvaluatedKey"], **kwargs)
            items.extend(response.get("Items", []))
    except (ClientError, BotoCoreError) as exc:
        _fail("reading history", exc)
    return [_clean(i) for i in items]


def clear_cache():
    _books_cache["items"], _books_cache["time"] = None, 0.0
