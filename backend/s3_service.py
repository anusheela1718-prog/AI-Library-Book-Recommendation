"""
s3_service.py - Everything that talks to Amazon S3.

Used for:
  * reading dataset/books.csv (fallback when the Books table is empty)
  * reading / writing the small model snapshot  model/tfidf_model.json
"""
import csv
import io
import json
import logging

import config
from errors import ServiceUnavailableError

logger = logging.getLogger()

try:  # boto3 exists on Lambda. The import is guarded so unit tests run without it.
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:  # pragma: no cover
    boto3 = None

    class ClientError(Exception):
        pass

    class BotoCoreError(Exception):
        pass

_client = None


def _s3():
    """Create the S3 client once and reuse it (faster on warm Lambda)."""
    global _client
    if boto3 is None:
        raise ServiceUnavailableError("boto3 is not installed.")
    if _client is None:
        _client = boto3.client("s3", region_name=config.AWS_REGION)
    return _client


def normalize_book(row):
    """Convert a CSV row (book_id, image_url ...) into the API book format (bookId, imageUrl ...)."""
    return {
        "bookId": (row.get("book_id") or row.get("bookId") or "").strip(),
        "title": (row.get("title") or "").strip(),
        "author": (row.get("author") or "").strip(),
        "category": (row.get("category") or "").strip(),
        "subject": (row.get("subject") or "").strip(),
        "keywords": (row.get("keywords") or "").strip(),
        "description": (row.get("description") or "").strip(),
        "imageUrl": (row.get("image_url") or row.get("imageUrl") or "").strip(),
    }


def parse_books_csv(text):
    """Parse CSV text into a list of book dicts."""
    reader = csv.DictReader(io.StringIO(text))
    books = [normalize_book(r) for r in reader]
    return [b for b in books if b["bookId"]]


def load_books_from_s3():
    """Read dataset/books.csv from the S3 bucket."""
    if not config.S3_BUCKET_NAME:
        return []
    try:
        obj = _s3().get_object(Bucket=config.S3_BUCKET_NAME, Key=config.S3_BOOKS_KEY)
        text = obj["Body"].read().decode("utf-8-sig")
        return parse_books_csv(text)
    except (ClientError, BotoCoreError) as exc:
        logger.error("S3 read failed: %s", exc)
        raise ServiceUnavailableError("Could not read the book dataset from S3.")


def save_model_snapshot(snapshot):
    """Write the TF-IDF model summary to model/tfidf_model.json"""
    try:
        _s3().put_object(
            Bucket=config.S3_BUCKET_NAME,
            Key=config.S3_MODEL_KEY,
            Body=json.dumps(snapshot).encode("utf-8"),
            ContentType="application/json",
        )
    except (ClientError, BotoCoreError) as exc:
        logger.error("S3 write failed: %s", exc)
        raise ServiceUnavailableError("Could not save the model file to S3.")


def load_model_snapshot():
    """Read model/tfidf_model.json (returns None if it does not exist)."""
    try:
        obj = _s3().get_object(Bucket=config.S3_BUCKET_NAME, Key=config.S3_MODEL_KEY)
        return json.loads(obj["Body"].read().decode("utf-8"))
    except (ClientError, BotoCoreError):
        return None
