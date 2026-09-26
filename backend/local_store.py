"""
local_store.py - A tiny in-memory replacement for DynamoDB.

Used ONLY when USE_LOCAL_STORAGE=true (running on your own PC without AWS).
Data comes from dataset/books.csv, students.json and reading_history.json.
Data added while running is lost when you stop the server.
"""
import json
import os
import uuid
from datetime import datetime, timezone

from s3_service import parse_books_csv

DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dataset")

_books = []
_students = {}
_history = []
_loaded = False


def _load():
    global _loaded, _books, _students, _history
    if _loaded:
        return
    with open(os.path.join(DATASET_DIR, "books.csv"), encoding="utf-8-sig") as f:
        _books = parse_books_csv(f.read())
    with open(os.path.join(DATASET_DIR, "students.json"), encoding="utf-8") as f:
        _students = {s["studentId"]: s for s in json.load(f)}
    with open(os.path.join(DATASET_DIR, "reading_history.json"), encoding="utf-8") as f:
        _history = json.load(f)
    _loaded = True


def get_all_books():
    _load()
    return list(_books)


def get_book(book_id):
    _load()
    return next((b for b in _books if b["bookId"] == book_id), None)


def get_student(student_id):
    _load()
    return _students.get(student_id)


def save_student(student):
    _load()
    _students[student["studentId"]] = student
    return student


def add_history(student_id, book_id, rating=None):
    _load()
    item = {
        "historyId": "H" + uuid.uuid4().hex[:12],
        "studentId": student_id,
        "bookId": book_id,
        "selectedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }
    if rating is not None:
        item["rating"] = rating
    _history.append(item)
    return item


def get_history(student_id):
    _load()
    items = [h for h in _history if h["studentId"] == student_id]
    return sorted(items, key=lambda h: h["selectedAt"], reverse=True)
