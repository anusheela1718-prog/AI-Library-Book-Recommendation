"""
config.py - All settings in ONE place.

Values are read from environment variables. On AWS Lambda you set them in
Configuration > Environment variables. If a variable is missing, a safe
default is used, so the code still runs.

NEVER put AWS access keys here. Lambda gets its permissions from an IAM role.
"""
import os

# AWS region (Lambda sets AWS_REGION automatically). Default = Mumbai.
AWS_REGION = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "ap-south-1"

# DynamoDB table names
STUDENTS_TABLE = os.environ.get("DYNAMODB_STUDENTS_TABLE", "Students")
BOOKS_TABLE = os.environ.get("DYNAMODB_BOOKS_TABLE", "Books")
HISTORY_TABLE = os.environ.get("DYNAMODB_HISTORY_TABLE", "ReadingHistory")
HISTORY_INDEX = os.environ.get("DYNAMODB_HISTORY_INDEX", "studentId-index")

# S3 bucket (used for the books.csv fallback and the model snapshot)
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "")
S3_BOOKS_KEY = "dataset/books.csv"
S3_MODEL_KEY = "model/tfidf_model.json"

# Recommendation settings
TOP_N = 5                       # how many books to return
BOOKS_CACHE_SECONDS = 300       # keep book list in memory for 5 minutes (faster)

# Local mode: run WITHOUT AWS (uses dataset/ files). Only for testing on your PC.
USE_LOCAL_STORAGE = os.environ.get("USE_LOCAL_STORAGE", "false").lower() == "true"
