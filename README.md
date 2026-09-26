# AI-Based Library Book Recommendation System ("AI LIBRARY")

A serverless web application on AWS that recommends the **top 5 library books** to a student using
**content-based filtering (TF-IDF + cosine similarity)** on the student's interests, subjects and reading history.

> Everything here runs in two ways: **locally on your PC (no AWS needed)** for practice, and **on AWS** for the real deployment.

## 1. Project title
AI-Based Library Book Recommendation System

## 2. Project overview
Students choose their interests (Java, AI, Cloud...) and subjects. The backend (AWS Lambda) reads the books from DynamoDB,
turns every book and the student profile into TF-IDF vectors, measures cosine similarity and returns the 5 best books with a
match score. When the student selects a book it is saved as reading history and used the next time.

## 3. Problem statement
College libraries hold thousands of books. Students waste time searching, often do not know which book fits their interest,
and the library catalogue gives the same list to everyone. A personalized, automatic suggestion system is needed.

## 4. Objectives
- Recommend relevant books from interests, subjects, categories, keywords, descriptions and history.
- Use a real ML method (TF-IDF + cosine similarity), not random output.
- Store data in DynamoDB and files in S3; run the backend serverless (Lambda + API Gateway).
- Keep it simple, low cost and easy to explain in a viva.

## 5. Features
Student profile form - interest and subject selection - Top 5 recommendations with match score and "matched on" words -
book details page with optional rating - reading history - browse and search all 108 books - recommendations improve after
book selection - works for new students - friendly error messages - responsive UI.

## 6. Technology stack
| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript (no framework) |
| Backend | Python 3.12, AWS Lambda, Boto3 |
| API | Amazon API Gateway (HTTP API), REST + JSON |
| Database | Amazon DynamoDB |
| Storage | Amazon S3 |
| AI/ML | TF-IDF + cosine similarity (pure Python) |
| Security | IAM role (no keys in code) |

## 7. AWS services
| Service | Job in this project |
|---|---|
| S3 | Hosts the website, book cover images, dataset (`books.csv`) and model file |
| DynamoDB | Stores Students, Books, ReadingHistory |
| Lambda | Runs the Python backend and the recommendation engine |
| API Gateway | Gives the frontend a public HTTPS URL and forwards requests to Lambda |
| IAM | Gives Lambda only the permissions it needs; CloudWatch Logs receives its logs |

## 8. AI/ML algorithm
1. **Book profile** = category + subject (x2) + keywords (x2) + title + description.
2. **TF-IDF**: TF = `1 + log(count)`, IDF = `log((1+N)/(1+df)) + 1`. Rare words weigh more.
3. **Student profile**: interests (x3) + subjects (x2) -> interest vector; selected books -> average history vector
   (rated 4-5 count double, rated 1-2 ignored).
4. **Cosine similarity** = `(A . B) / (|A| |B|)`.
5. **Personalized score** = `0.7 x sim(interests, book) + 0.3 x sim(history, book)`. New student: `sim(interests, book)` only.
6. Remove already-read books, sort by score, return top 5 (only score > 0). If nothing matches, an empty list and a friendly message.

Code: `backend/recommendation_engine.py`. A short synonym table expands "AI" -> "artificial intelligence", "ML" -> "machine learning" etc.
The **Match Score %** is the cosine similarity x 100. Text vectors rarely reach 100%; 30-70% is a strong match. The ranking is what matters.

## 9. System architecture
```
Student -> Browser (HTML/CSS/JS on S3 website)
        -> API Gateway (HTTPS)
        -> Lambda (Python) --- IAM role
              |-- DynamoDB: Students, Books, ReadingHistory
              |-- S3: dataset/books.csv, model/ (fallback + model file)
              '-- Recommendation engine (TF-IDF + cosine)
        -> Top 5 books -> Browser
```
More detail: `docs/architecture.md`.

## 10. Folder structure
```
AI-Library-Book-Recommendation/
├── README.md   .env.example   .gitignore
├── frontend/   index.html login.html signup.html dashboard.html browse-books.html book-details.html
│               recommendations.html history.html profile.html about.html
│               css/{base,auth,dashboard,books,profile}.css
│               js/{config,api,app,auth,nav,login,signup,dashboard,books,book-details,recommendations,history,profile}.js
│               images/ (108 covers)  assets/
├── backend/    lambda_function.py recommendation_engine.py dynamodb_service.py s3_service.py
│               config.py errors.py local_store.py local_server.py requirements.txt  tests/
├── dataset/    books.csv (108)  students.json (10)  reading_history.json (14)
├── aws/        dynamodb/ iam/ lambda/ api-gateway/ s3/   (ready-made JSON + scripts)
├── scripts/    generate_dataset.py seed_dynamodb.py upload_to_s3.py package_lambda.py deploy.sh
└── docs/       architecture, database-design, api-documentation, deployment-guide, testing,
                viva-questions, project-report, ppt-content, demo-guide
```

## 11. Database design
| Table | Partition key | Attributes |
|---|---|---|
| Students | studentId | name, department, year, interests (list), subjects (list) |
| Books | bookId | title, author, category, subject, keywords, description, imageUrl |
| ReadingHistory | historyId (+ GSI `studentId-index`: studentId, selectedAt) | studentId, bookId, selectedAt, rating (optional) |

Details and reasons: `docs/database-design.md`.

## 12. API documentation
| Method & path | Purpose |
|---|---|
| GET /health | API is alive |
| GET /books?q=&category= | List / search books |
| GET /books/{bookId} | One book |
| POST /students | Create / update a student |
| GET /students/{studentId} | Read a student |
| POST /recommendations | Top 5 personalized books |
| POST /history | Save "student selected this book" |
| GET /history/{studentId} | Student's reading history |

Errors are always `{"error": "message"}` with status 400 / 404 / 405 / 500 / 503. Full examples: `docs/api-documentation.md`.

## 13. Local setup (no AWS needed - do this first!)
```bash
# Python 3.9+ required (python --version)
cd AI-Library-Book-Recommendation/backend
python local_server.py            # Windows: python local_server.py  |  Mac/Linux: python3 local_server.py
# open http://localhost:8000
```
The site opens on the public landing page. Click **Create Account**, fill in a Student ID (e.g. `TEST1`), name, email,
password and your interests/subjects, and you're taken straight to the Dashboard. Data added while the server is
running is kept only in memory (lost on restart) unless you deploy to real AWS (Section 14/15).
Run the tests: `cd backend && python -m unittest discover -s tests -v`.

### Frontend pages (multi-page app)
| Page | File | Needs sign-in? |
|---|---|---|
| Landing | `index.html` | No |
| Sign In | `login.html` | No |
| Create Account | `signup.html` | No |
| Dashboard | `dashboard.html` | Yes |
| Browse Books | `browse-books.html` | Yes |
| Book Details | `book-details.html?id=B001` | Yes |
| Recommendations | `recommendations.html` | Yes |
| Reading History | `history.html` | Yes |
| Profile | `profile.html` | Yes |
| About / Help | `about.html` | Either |

**Sign-in is a browser-only demo layer** (`frontend/js/auth.js`): it stores an email/password record in `localStorage`
purely so the multi-page app has a working Sign In / Sign Up / Logout flow to demonstrate. It is clearly commented as
not production-grade and is not connected to AWS. The student **profile** (interests, subjects) created at sign-up
*is* saved for real, through `Api.saveStudent()` into DynamoDB, and every recommendation still comes from the real
backend TF-IDF + cosine similarity engine in `backend/recommendation_engine.py` - nothing in the backend was changed.
Protected pages call `Auth.requireAuth()` (in `js/nav.js`) and redirect to `login.html` if no one is signed in.

CSS is split into `css/base.css` (shared design tokens, nav, buttons, forms, cards) plus one small file per page group:
`auth.css` (landing/login/signup), `dashboard.css`, `books.css` (browse/details/recommendations/history), `profile.css`.

## 14. AWS setup
Follow **`docs/deployment-guide.md`** step by step (Console clicks + CLI commands). Summary of what you will create:
S3 bucket -> 3 DynamoDB tables -> IAM role `AILibraryLambdaRole` -> Lambda `AILibraryBackend` -> HTTP API `ai-library-api`.
Things you must replace: **region** (`ap-south-1`), **bucket name**, **account ID**, **API URL** in `frontend/js/config.js`.

## 15. Deployment (order)
1 AWS account -> 2 `aws configure` -> 3 S3 bucket -> 4 upload dataset -> 5 DynamoDB tables + seed -> 6 IAM role ->
7 create Lambda -> 8 package ZIP -> 9 deploy ZIP -> 10 API Gateway -> 11 CORS -> 12 put API URL in `config.js` ->
13 upload website to S3 + enable hosting -> 14 test. Later updates: `BUCKET=name bash scripts/deploy.sh all`.

## 16. Testing
- 46 automated tests (`backend/tests/`): engine maths, ranking, history, and all API cases (valid/invalid student, empty interests,
  new student, history, no match, DynamoDB failure, invalid request...). They use mocks, so no AWS is needed.
- Manual test table and expected results: `docs/testing.md`.

## 17. Troubleshooting
| Problem | Fix |
|---|---|
| Browser: "Cannot reach the server" | Wrong `API_BASE_URL` in `js/config.js` (no trailing slash) or CORS not enabled. Re-upload `config.js`. |
| Console shows CORS error | API Gateway > CORS > allow origin `*`, methods GET/POST/OPTIONS, header `content-type`; save. |
| API returns 503 "database temporarily unavailable" | Table name/region mismatch or IAM policy missing. Check Lambda env vars and CloudWatch logs. |
| `Runtime.ImportModuleError` | ZIP has files inside a folder. Use `python scripts/package_lambda.py` (files at ZIP root). |
| Website shows 403 Forbidden | Turn off Block Public Access on the bucket and add `aws/s3/bucket-policy.json`. |
| Empty recommendations | Books table empty. Run `python scripts/seed_dynamodb.py`. |
| `NoSuchBucket` / name taken | Bucket names are global. Add your name + numbers. |
More in `docs/deployment-guide.md` (Common errors).

## 18. Future enhancements
Login (Amazon Cognito), admin page to add books, collaborative filtering, real cover images, CloudFront HTTPS, book availability
(issue/return), SageMaker or embeddings (BERT) for smarter text matching, email notifications, analytics dashboard.

## 19. Limitations
Text-based matching only (no meaning beyond words), small demo dataset (108 demo books), no login (Student ID is trusted),
website is HTTP unless CloudFront is added, scores are cosine values (not probabilities), books are loaded fully for each
calculation (fine for hundreds/few thousand books).

## 20. Team / project explanation
Final-year BCA project. Modules: (1) Student profile, (2) Interest selection, (3) Book catalogue, (4) Recommendation engine,
(5) Reading history, (6) Cloud backend and database. One-line explanation for the examiner:
*"The system converts books and the student's interests into TF-IDF vectors, finds the books with highest cosine similarity,
and runs serverless on AWS with DynamoDB for data and S3 for files."*
All book titles, authors and descriptions are original demo data.
