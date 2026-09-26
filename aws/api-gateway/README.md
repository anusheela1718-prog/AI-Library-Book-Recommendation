# API Gateway (HTTP API)

One `$default` route sends every request to the Lambda function, and `lambda_function.py` routes it:

GET /health | GET /books | GET /books/{bookId} | POST /students | GET /students/{studentId} |
POST /recommendations | POST /history | GET /history/{studentId}

CORS is enabled on the API (allow origin `*`, methods GET/POST/OPTIONS, header Content-Type) and Lambda also
returns the CORS headers. For a stricter setup, replace `*` with your S3 website URL.
