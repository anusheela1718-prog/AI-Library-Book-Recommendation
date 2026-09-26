"""
upload_to_s3.py - Uploads the website, the dataset and the model file to your S3 bucket.

    python scripts/upload_to_s3.py --bucket YOUR-BUCKET-NAME --region ap-south-1

Bucket layout created:
    /index.html, recommendations.html ...   (from frontend/)
    /css  /js  /assets  /images
    /dataset/books.csv
    /model/tfidf_model.json
Edit frontend/js/config.js (API URL) BEFORE running this script.
"""
import argparse
import csv
import json
import mimetypes
import os
import sys

try:
    import boto3
except ImportError:
    sys.exit("boto3 is missing. Run:  pip install boto3")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend"))
import recommendation_engine as engine  # noqa: E402
from s3_service import parse_books_csv  # noqa: E402

mimetypes.add_type("image/svg+xml", ".svg")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bucket", required=True)
    p.add_argument("--region", default=os.environ.get("AWS_REGION", "ap-south-1"))
    args = p.parse_args()
    s3 = boto3.client("s3", region_name=args.region)

    count = 0
    frontend = os.path.join(ROOT, "frontend")
    for folder, _, files in os.walk(frontend):
        for name in files:
            if name.endswith(".txt"):
                continue
            path = os.path.join(folder, name)
            key = os.path.relpath(path, frontend).replace(os.sep, "/")
            ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
            extra = {"ContentType": ctype}
            if key.endswith((".html", ".js", ".css")):
                extra["CacheControl"] = "no-cache"          # always fetch the latest version
            s3.upload_file(path, args.bucket, key, ExtraArgs=extra)
            count += 1
    print(f"Website files uploaded: {count}")

    s3.upload_file(os.path.join(ROOT, "dataset", "books.csv"), args.bucket, "dataset/books.csv",
                   ExtraArgs={"ContentType": "text/csv"})
    print("Uploaded dataset/books.csv")

    with open(os.path.join(ROOT, "dataset", "books.csv"), encoding="utf-8-sig") as f:
        books = parse_books_csv(f.read())
    snapshot = engine.build_model_snapshot(books)
    s3.put_object(Bucket=args.bucket, Key="model/tfidf_model.json",
                  Body=json.dumps(snapshot).encode("utf-8"), ContentType="application/json")
    print(f"Uploaded model/tfidf_model.json (vocabulary: {snapshot['vocabularySize']} words)")
    print("Done. Website URL: http://%s.s3-website.%s.amazonaws.com" % (args.bucket, args.region))


if __name__ == "__main__":
    main()
