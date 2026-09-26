# Architecture

```
 STUDENT
    |  (browser)
    v
 FRONTEND  (HTML/CSS/JS)  -- hosted on Amazon S3 static website
    |  fetch() JSON over HTTPS
    v
 AMAZON API GATEWAY (HTTP API)   <- public URL, CORS
    |  invokes
    v
 AWS LAMBDA  (Python 3.12)   <- runs with IAM role AILibraryLambdaRole
    |-- dynamodb_service.py --> DYNAMODB  (Students, Books, ReadingHistory)
    |-- s3_service.py -------> S3         (dataset/books.csv, model/tfidf_model.json)
    '-- recommendation_engine.py  (TF-IDF + cosine similarity)
    v
 TOP 5 PERSONALIZED BOOK RECOMMENDATIONS  -> JSON -> browser
```

## What each service does
| Service | Role |
|---|---|
| **S3** | Static website hosting; book cover images; `dataset/books.csv`; `model/tfidf_model.json`. |
| **DynamoDB** | NoSQL database: students, books and reading history. Fast key lookups, pay per request. |
| **Lambda** | Runs backend code only when a request comes (serverless). No server to manage. |
| **API Gateway** | Front door: public URL, routing, CORS, sends requests to Lambda. |
| **IAM** | Permissions. Lambda role can only touch the 3 tables and `dataset/`, `model/` in S3. |
| **CloudWatch Logs** | Automatic logs from Lambda (used for debugging). |

## Request flow: POST /recommendations
1. Browser sends `{studentId, interests, subjects}`.
2. API Gateway forwards the event to Lambda.
3. `lambda_function.py` validates the input.
4. `dynamodb_service.py` loads the student's history and all books (books cached 5 min).
5. `recommendation_engine.py` builds TF-IDF vectors, computes cosine similarities, ranks books.
6. Lambda returns the top 5 as JSON; the browser draws the cards.

## Code modules
| File | Responsibility |
|---|---|
| `lambda_function.py` | Routing, validation, HTTP status codes, CORS, logging |
| `recommendation_engine.py` | Tokenising, TF-IDF, cosine, personalized score |
| `dynamodb_service.py` | All DynamoDB reads/writes (with cache and error handling) |
| `s3_service.py` | CSV fallback and model file in S3 |
| `config.py` | Settings from environment variables |
| `errors.py` | ValidationError, NotFoundError, ServiceUnavailableError |
| `local_store.py`, `local_server.py` | Run everything on your PC without AWS |

## Why this design
Serverless = no server maintenance, almost free for a demo, scales automatically. Pure-Python engine = no heavy
libraries, so the Lambda ZIP is only ~12 KB and deployment cannot fail on a missing layer.
