# Project report content

## A. Abstract
Finding the right book in a large library is difficult for students because a normal catalogue shows the same results to everyone.
This project presents an AI-Based Library Book Recommendation System that suggests personalized books to students according to their
interests, subjects and reading history. The system uses a content-based recommendation method. Each book is described by its category,
subject, keywords and description, and these texts are converted into numerical vectors with the TF-IDF technique. The student's interests
and previously selected books are converted in the same way. Cosine similarity is then calculated between the student profile and every
book, and the five most similar books are displayed with a match score. The application is built with HTML, CSS and JavaScript for the
frontend and Python for the backend. It is deployed on Amazon Web Services using S3 for hosting and files, DynamoDB for data, AWS Lambda
and API Gateway for the serverless API, and IAM for security. When a student selects a book, it is saved as reading history and used to
improve later recommendations. The system is simple, low cost, tested with automated test cases and suitable for real college libraries.

## B. Introduction
A library is the centre of learning in a college. Modern libraries hold thousands of printed and digital books on many subjects, such as
programming, databases, networks and artificial intelligence. When students visit the library or an online catalogue, they usually search by title
or author. This works only when the student already knows what to look for. Beginners often do not know which book suits their level and interest,
and they spend a lot of time browsing or ask friends and staff for advice.

Recommendation systems solve a similar problem in online shopping and video platforms. They study what a user likes and suggest new items
automatically. Applying the same idea to a library can save time, increase book usage and help students learn faster.

This project develops such a system for BCA students. The student enters an ID, selects interests such as Java, Python, Machine Learning or Cloud
Computing, and chooses subjects. The backend compares this profile with all books using TF-IDF and cosine similarity, which are simple and well known
text-mining techniques. The system also remembers the books the student selected and uses them for the next recommendation.

To make the project practical, it uses cloud services from AWS. The website is stored in Amazon S3, the data is stored in Amazon DynamoDB, the logic
runs in AWS Lambda, and Amazon API Gateway connects the website to the backend. Because the design is serverless, there is no server to maintain
and the cost is very low. The result is a complete, deployable application that demonstrates machine learning, cloud computing and web development together.

## C. Problem statement
Students cannot easily find suitable books in a large library because the catalogue offers only manual, title-based search and gives the same result to every
student. The library needs an automatic system that understands a student's interests, subjects and reading history and recommends the most relevant books.

## D. Existing system
- Manual search in registers or a basic online catalogue.
- Search by title, author or keyword only.
- No personalization; every student sees the same list.
- Reading history is not used.
- Students depend on librarians or friends for suggestions.
- Many useful books are never discovered.

## E. Proposed system
- A web application where the student enters ID, interests and subjects.
- A content-based recommendation engine (TF-IDF + cosine similarity) calculates a personalized score.
- Top 5 books are shown with title, author, category, subject, description and match score.
- Selected books are stored in DynamoDB and used in later recommendations.
- New students still get recommendations from their interests.
- Cloud-based, serverless and low cost (S3, DynamoDB, Lambda, API Gateway, IAM).

## F. Objectives
1. Build a personalized book recommendation system.
2. Use TF-IDF and cosine similarity for real, explainable AI.
3. Use reading history to improve results.
4. Store data in DynamoDB and files in S3.
5. Deploy a serverless backend with Lambda and API Gateway.
6. Provide a simple, responsive user interface.
7. Handle errors and validate input.

## G. Scope
Covers academic/technical books for BCA students (programming, web, databases, networks, AI/ML, cloud, security, software engineering,
emerging technologies, architecture). Works for one college library with hundreds to a few thousand books. Out of scope: user login,
book issue/return, payment, digital book reading, collaborative filtering.

## H. Methodology
1. Requirement study and dataset creation (108 demo books).
2. Design of architecture and database.
3. Implementation of the recommendation engine in Python.
4. Implementation of Lambda API and DynamoDB/S3 services.
5. Frontend development with HTML/CSS/JavaScript.
6. Local testing with automated tests.
7. Deployment on AWS and end-to-end testing.

**Algorithm steps:** clean text -> tokens -> TF (`1+log count`) -> IDF (`log((1+N)/(1+df))+1`) -> TF-IDF vectors -> normalise ->
cosine similarity -> combine interest and history scores -> sort -> top 5.

## I. System architecture
Student -> Frontend (S3 website) -> API Gateway -> Lambda -> DynamoDB -> Recommendation engine -> Top 5 books. S3 stores the dataset, images
and model file; IAM controls permissions; CloudWatch stores logs. (Diagram: `docs/architecture.md`.)

## J. Modules
1. **Student Profile module** - ID, name, department, year; saved in Students table.
2. **Interest Selection module** - interests and subjects.
3. **Book Catalogue module** - browse, search, details.
4. **Recommendation Engine module** - TF-IDF, cosine similarity, ranking.
5. **Reading History module** - store and show selected books, optional rating.
6. **Cloud Backend module** - Lambda, API Gateway, DynamoDB, S3, IAM.

## K. Functional requirements
- FR1 The system shall accept Student ID, name, department, year.
- FR2 The system shall accept interests and subjects.
- FR3 The system shall retrieve books from DynamoDB.
- FR4 The system shall calculate similarity between student profile and books.
- FR5 The system shall show the top 5 books with match scores.
- FR6 The system shall show book details.
- FR7 The system shall let the student select a book and store it in history.
- FR8 The system shall use history in future recommendations.
- FR9 The system shall work for students with no history.
- FR10 The system shall show friendly error messages.

## L. Non-functional requirements
- **Performance:** response within 1-2 seconds for 100-1000 books.
- **Availability:** serverless AWS services, no server maintenance.
- **Security:** IAM least privilege, no keys in code, input validation.
- **Usability:** simple responsive UI for mobile and desktop.
- **Maintainability:** modular code, comments, tests.
- **Cost:** within the AWS free tier / very low cost.
- **Scalability:** Lambda and DynamoDB scale automatically.

## M. Hardware requirements
- Development PC: 4 GB RAM (8 GB recommended), dual-core processor, 2 GB free disk, internet connection.
- User device: any phone, tablet or PC with a web browser.
- Server: none (AWS serverless).

## N. Software requirements
Windows/Linux/macOS, Python 3.9+, AWS CLI v2, boto3, modern browser (Chrome/Edge/Firefox), VS Code, Git Bash (Windows), AWS account.

## O. AWS services explanation
- **S3:** stores website files, images, `books.csv`, model JSON.
- **DynamoDB:** NoSQL tables Students, Books, ReadingHistory.
- **Lambda:** runs the Python backend without a server.
- **API Gateway:** creates the public REST endpoint and CORS.
- **IAM:** role with minimum permissions for Lambda.
- **CloudWatch Logs:** collects Lambda logs.

## P. AI/ML algorithm explanation
**Content-based filtering** recommends items similar to what the user likes.
**TF-IDF:** `TF = 1 + ln(count)`, `IDF = ln((1+N)/(1+df)) + 1`, weight = TF x IDF. Words that appear in every book get low weight, rare meaningful words get high weight.
**Cosine similarity:** `cos = (A.B)/(|A||B|)`; between 0 and 1.
**Student profile:** interests x3 + subjects x2 (interest vector); average of selected books (history vector).
**Final score:** `0.7 x cos(interest, book) + 0.3 x cos(history, book)`; new student uses interests only.
**Example:** interest "Machine Learning" -> ML books score about 0.58 while Deep Learning books score about 0.24, so ML books are ranked first.

## Q. Database design
Tables: Students (PK studentId), Books (PK bookId), ReadingHistory (PK historyId, GSI studentId-index). Attribute lists are in `docs/database-design.md`.

## R. Testing
46 automated unit/API tests plus 12 manual test cases (valid/invalid student, empty interests, multiple interests, new student, history, no match,
book selection, reading history, API failure, DynamoDB failure, invalid request). All automated tests pass. Details: `docs/testing.md`.

## S. Results
- New student with interest "Machine Learning" and subject "Artificial Intelligence": the top four results were the four Machine Learning books (about 56-58% match), followed by an AI book (about 30%).
- After selecting one ML book, the selected book disappeared, the other ML books rose to about 65-66% and a Deep Learning book entered the top 5, showing that history changes the result.
- Invalid input returns clear 400 messages; DynamoDB failure returns 503 without crashing.
- Add your own screenshots of the deployed website here.

## T. Future enhancements
Amazon Cognito login, admin page for adding books, collaborative filtering (hybrid system), sentence embeddings / SageMaker, CloudFront HTTPS,
book availability and issue/return, email alerts, usage analytics, multi-language support.

## U. Conclusion
The project delivers a working AI library recommendation system on AWS. It combines TF-IDF, cosine similarity, student interests and reading history to
give personalized top-5 recommendations. The serverless design with S3, DynamoDB, Lambda, API Gateway and IAM keeps the cost low and the maintenance
minimal. The system is tested, secure by design, and can be extended with more books and advanced machine learning in the future.
