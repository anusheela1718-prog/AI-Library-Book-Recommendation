# Testing

## A. Automated tests (no AWS needed)
```bash
cd backend
python -m unittest discover -s tests -v
```
Expected: `Ran 46 tests ... OK`.
- `tests/test_recommendation_engine.py` - tokenizer, TF-IDF/IDF, cosine, ranking, history, no-match, top-N.
- `tests/test_api.py` - every API endpoint with DynamoDB replaced by mocks.

## B. Test cases (manual on the website, or with curl)
Replace `API` with your API URL (locally `http://localhost:8000`).

| # | Test case | Input / action | Expected result |
|---|---|---|---|
| 1 | Valid student | `POST /recommendations` `{"studentId":"ST001","interests":["Java","AI"],"subjects":["Programming"]}` | 200, up to 5 books, scores sorted high to low, Java books first |
| 2 | Invalid student | `{"studentId":"bad id!!","interests":["Java"]}` or missing studentId | 400 `studentId ...` message |
| 3 | Empty interests | `{"studentId":"NEW1","interests":[],"subjects":[]}` (no history) | 400 "Please select at least one interest or subject." |
| 4 | Multiple interests | `["Java","Machine Learning","Cloud Computing"]` | 200, mix of Java, ML and Cloud books |
| 5 | New student, no history | New id `NEW2` with interests `["SQL"]` | 200, `historyCount: 0`, SQL books |
| 6 | Existing student with history | `ST001` (has history) | 200, `historyCount >= 1`, already-read books are not listed |
| 7 | No matching books | interests `["xyzabc"]` | 200, `recommendations: []`, message "No matching books were found..." |
| 8 | Book selection | `POST /history` `{"studentId":"ST001","bookId":"B003","rating":5}` | 201 with historyId; unknown book -> 404; rating 9 -> 400 |
| 9 | Reading history | `GET /history/ST001` | 200, list newest first with titles; new student -> `count: 0` |
| 10 | API failure | `GET /nothing` ; `GET /recommendations` | 404 route error ; 405 wrong method |
| 11 | DynamoDB failure | Remove DynamoDB permission from the role (or wrong table name) and call `/recommendations` | 503 "The database is temporarily unavailable..." (site shows a red message, no crash). Restore the policy afterwards. |
| 12 | Invalid API request | body `{not json` , empty body, `"interests": 123` | 400 with clear message |

Extra: `GET /health` -> 200; `OPTIONS /recommendations` -> 200 with CORS headers; `GET /books?q=aws` -> AWS books.

## C. Frontend checks
| Check | Expected |
|---|---|
| Submit form with empty ID | Red message "Please enter your Student ID." |
| Submit with no interest and no subject | Red message asking to select one |
| Recommendations page without profile | Message with link to profile page |
| Select Book | Green toast; History page shows it |
| Refresh after selection | Results change; selected book not repeated |
| Phone width (Chrome DevTools -> mobile view) | Single column, no horizontal scroll |
| Wrong API URL in config.js | Red message "Cannot reach the server..." |

## D. Personalization proof (good for the demo)
1. New student, interest `Machine Learning`, subject `Artificial Intelligence` -> top results are ML books (about 58%).
2. Select "Machine Learning Exam and Interview Guide".
3. Refresh -> the read book disappears; other ML books rise (about 66%) and Deep Learning / AI books appear from history similarity.
