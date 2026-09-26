# PPT content (12 slides)

Use a clean template. Big fonts. Screenshots on slide 11 (home page, recommendations page, history page, DynamoDB items, Lambda test, API health).

---
### Slide 1 - Title
**Bullets**
- AI-Based Library Book Recommendation System
- Final Year BCA Project
- Your name | Register No. | Guide name | College | Year 2026

**Say:** "Good morning. My project is an AI-based library book recommendation system built on AWS."

### Slide 2 - Introduction
- Libraries have thousands of books
- Students find it hard to choose the right book
- AI can suggest books using interests and reading history
- Built with Python, AWS Lambda, DynamoDB, S3

**Say:** "Students often do not know which book fits their interest. My system recommends the best five books automatically."

### Slide 3 - Problem Statement
- Manual search is slow
- Same catalogue for everyone
- No use of student interests or history
- Good books stay unused

**Say:** "Today's catalogue is not personal. I wanted a personalized and automatic suggestion."

### Slide 4 - Objectives
- Recommend top 5 personalized books
- Use TF-IDF and cosine similarity
- Store data in DynamoDB, files in S3
- Serverless, low-cost, easy to use

**Say:** "The main goal is a working AI recommendation on a real cloud, with simple design."

### Slide 5 - Existing System
- Manual catalogue search / registers
- Keyword search only
- No personalization, no learning from history
- Depends on librarian's help

**Say:** "Existing systems only search by title. They do not understand a student's interests."

### Slide 6 - Proposed System
- Student enters ID, interests and subjects
- System compares interests with book details
- Returns top 5 books with match score
- Saves selections and improves next time

**Say:** "The proposed system understands interests and improves with reading history."

### Slide 7 - System Architecture
- Student -> Website (S3) -> API Gateway -> Lambda -> DynamoDB -> Recommendation engine -> Top 5 books
- S3 also stores dataset, images, model file
- IAM protects access

**Say:** "The browser calls API Gateway, which triggers Lambda. Lambda reads DynamoDB, runs the engine and returns five books." (Draw the diagram from `docs/architecture.md`.)

### Slide 8 - Technologies and AWS Services
- Frontend: HTML, CSS, JavaScript
- Backend: Python, Boto3
- S3: website, images, dataset
- DynamoDB: Students, Books, ReadingHistory
- Lambda + API Gateway: serverless API
- IAM: secure permissions

**Say:** "I used only five AWS services to keep the architecture simple and reliable."

### Slide 9 - AI/ML Recommendation Method
- Content-based filtering
- TF-IDF: gives importance to each word
- Cosine similarity: compares student profile and book
- Score = 0.7 x interests + 0.3 x history
- Sort and show top 5

**Say:** "Every book and the student profile become number vectors. The books with the highest cosine similarity are recommended. Reading history adds personalization."

### Slide 10 - Modules
- Student profile
- Interest selection
- Book catalogue and search
- Recommendation engine
- Reading history
- Cloud backend and database

**Say:** "The project has six modules, each easy to test separately."

### Slide 11 - Results / Screenshots
- Screenshot: home page and form
- Screenshot: Top 5 with match scores
- Screenshot: history and DynamoDB item
- 46 automated tests passed
- Recommendations change after selecting a book

**Say:** "This is the working system. For a Machine Learning interest the top books are ML books with about 58% match. After selecting a book the ranking changes."

### Slide 12 - Conclusion and Future Scope
- Working, deployed, personalized recommendation system
- Simple, low cost, scalable
- Future: login (Cognito), admin panel, embeddings, collaborative filtering, HTTPS with CloudFront

**Say:** "The project shows how AI and cloud can improve a library. Thank you. I am ready for questions."
