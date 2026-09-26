"""
seed_dynamodb.py - Loads the sample data into your DynamoDB tables.

Run from the project folder (after `aws configure` and creating the tables):
    pip install boto3
    python scripts/seed_dynamodb.py --region ap-south-1
"""
import argparse
import csv
import json
import os
import sys

try:
    import boto3
except ImportError:
    sys.exit("boto3 is missing. Run:  pip install boto3")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET = os.path.join(ROOT, "dataset")


def main():
    p = argparse.ArgumentParser(description="Seed DynamoDB with sample data")
    p.add_argument("--region", default=os.environ.get("AWS_REGION", "ap-south-1"))
    p.add_argument("--books-table", default=os.environ.get("DYNAMODB_BOOKS_TABLE", "Books"))
    p.add_argument("--students-table", default=os.environ.get("DYNAMODB_STUDENTS_TABLE", "Students"))
    p.add_argument("--history-table", default=os.environ.get("DYNAMODB_HISTORY_TABLE", "ReadingHistory"))
    args = p.parse_args()

    db = boto3.resource("dynamodb", region_name=args.region)

    # Books (CSV column names -> DynamoDB attribute names)
    with open(os.path.join(DATASET, "books.csv"), encoding="utf-8-sig", newline="") as f:
        books = [{
            "bookId": r["book_id"], "title": r["title"], "author": r["author"], "category": r["category"],
            "subject": r["subject"], "keywords": r["keywords"], "description": r["description"],
            "imageUrl": r["image_url"],
        } for r in csv.DictReader(f)]
    with db.Table(args.books_table).batch_writer() as batch:
        for b in books:
            batch.put_item(Item=b)
    print(f"Books loaded: {len(books)}")

    with open(os.path.join(DATASET, "students.json"), encoding="utf-8") as f:
        students = json.load(f)
    with db.Table(args.students_table).batch_writer() as batch:
        for s in students:
            batch.put_item(Item=s)
    print(f"Students loaded: {len(students)}")

    with open(os.path.join(DATASET, "reading_history.json"), encoding="utf-8") as f:
        history = json.load(f)
    with db.Table(args.history_table).batch_writer() as batch:
        for h in history:
            batch.put_item(Item=h)
    print(f"Reading history loaded: {len(history)}")
    print("Done.")


if __name__ == "__main__":
    main()
