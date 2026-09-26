# API documentation

Base URL: `https://<api-id>.execute-api.<region>.amazonaws.com` (locally: `http://localhost:8000`)
All bodies are JSON. Every response has CORS headers. Errors look like `{"error":"message"}`.

| Status | Meaning |
|---|---|
| 200 / 201 | OK / created |
| 400 | Invalid input (missing studentId, empty interests, bad JSON) |
| 404 | Book / student / route not found |
| 405 | Wrong HTTP method for that path |
| 500 | Unexpected server error |
| 503 | DynamoDB/S3 temporarily unavailable |

## GET /health
`200 {"status":"ok","service":"AI Library Book Recommendation API"}`

## GET /books
Optional query: `q` (search title/author/subject/keywords), `category` (exact).
`200 {"count":108,"books":[{"bookId":"B001","title":"Java Fundamentals","author":"Ananya Rao","category":"Programming","subject":"Java","keywords":"...","description":"...","imageUrl":"images/B001.svg"}]}`

## GET /books/{bookId}
`200` book object, or `404 {"error":"Book B999 was not found."}`

## POST /students
```json
{"studentId":"ST001","name":"Aarav Kumar","department":"BCA","year":"3","interests":["Java","AI"],"subjects":["Programming"]}
```
`201` created (or `200` updated) with the saved student. `400` if `studentId`/`name` missing or invalid
(studentId: letters, digits, `-`, `_`, max 20).

## GET /students/{studentId}
`200` student, or `404`.

## POST /recommendations  (main endpoint)
Request:
```json
{"studentId":"ST001","interests":["Java","AI","Programming"],"subjects":["Computer Science"]}
```
Response `200`:
```json
{
  "studentId": "ST001",
  "interests": ["Java","AI","Programming"],
  "subjects": ["Computer Science"],
  "historyCount": 2,
  "recommendations": [
    {"bookId":"B003","title":"Java Advanced Concepts","author":"Priya Nair","category":"Programming","subject":"Java",
     "keywords":"...","description":"...","imageUrl":"images/B003.svg",
     "score":0.3812,"matchPercent":38,"matchedTerms":["java","programming"]}
  ]
}
```
- If `interests` and `subjects` are both empty, the saved student profile is used; if there is none and no history -> `400`.
- No matching book -> `200` with `"recommendations": []` and a `"message"`.

## POST /history
```json
{"studentId":"ST001","bookId":"B003","rating":5}
```
`rating` is optional (1-5). `201 {"historyId":"H...","studentId":"ST001","bookId":"B003","selectedAt":"2026-09-21T10:00:00Z","rating":5}`.
`404` if the book does not exist, `400` for invalid rating.

## GET /history/{studentId}
`200 {"studentId":"ST001","count":1,"history":[{"historyId":"H001","bookId":"B001","selectedAt":"...","rating":5,"title":"Java Fundamentals","author":"...","category":"Programming","subject":"Java","imageUrl":"images/B001.svg"}]}` (newest first; `count` 0 for new students)

## Test with curl
```bash
curl https://YOUR-API/health
curl -X POST https://YOUR-API/recommendations -H "Content-Type: application/json" \
     -d '{"studentId":"ST001","interests":["Java","AI"],"subjects":["Programming"]}'
```
