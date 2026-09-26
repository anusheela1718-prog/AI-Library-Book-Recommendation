# Lambda settings

| Setting | Value |
|---|---|
| Function name | AILibraryBackend |
| Runtime | Python 3.12 |
| Handler | `lambda_function.lambda_handler` |
| Role | AILibraryLambdaRole |
| Memory / Timeout | 256 MB / 15 seconds |
| Architecture | x86_64 |

Environment variables (see `environment.json`):
`DYNAMODB_STUDENTS_TABLE`, `DYNAMODB_BOOKS_TABLE`, `DYNAMODB_HISTORY_TABLE`, `S3_BUCKET_NAME`
(Do NOT add `AWS_REGION` - Lambda sets it automatically.)

**No layer needed**: boto3 is built into the Lambda Python runtime and the TF-IDF engine uses only the standard library.
Build the ZIP with `python scripts/package_lambda.py` -> `build/lambda.zip`.
