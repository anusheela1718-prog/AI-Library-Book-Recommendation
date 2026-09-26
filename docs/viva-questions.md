# Viva questions and short answers (50)

## A. Basics of AI / ML / recommendation
1. **What is AI?** Making computers do tasks that need human intelligence, like understanding, learning and deciding.
2. **What is Machine Learning?** A part of AI where computers learn patterns from data instead of being programmed with fixed rules.
3. **What is a recommendation system?** Software that suggests items (books, movies, products) a user is likely to like.
4. **Types of recommendation systems?** Content-based, collaborative filtering, and hybrid.
5. **What is content-based recommendation?** It recommends items similar to the user's interests by comparing item content (text, category, keywords).
6. **What is collaborative filtering?** It recommends what similar users liked. It needs many users; we do not use it.
7. **Why content-based for this project?** Works for a new library with few users, needs only book details, and is easy to explain.
8. **What is TF-IDF?** Term Frequency x Inverse Document Frequency. It gives a number to each word: high if the word is frequent in this book but rare in other books.
9. **What is TF?** How many times a word appears in one text. We use `1 + log(count)`.
10. **What is IDF?** How rare a word is across all books. Rare word = higher weight. Formula: `log((1+N)/(1+df)) + 1`.
11. **Why use TF-IDF?** Common words like "book" are unimportant; TF-IDF lowers them and highlights meaningful words like "pointers" or "lambda".
12. **What is cosine similarity?** It measures the angle between two vectors. Same direction = 1, nothing in common = 0.
13. **Why cosine similarity?** It ignores text length and only compares direction, so a long and a short description can still match.
14. **What is a vector?** A list of numbers. Here each number is the TF-IDF weight of one word.
15. **What is tokenization / stop words?** Splitting text into words / removing useless words like "the" and "and".

## B. How my project works
16. **How does the recommendation work?** Build TF-IDF vectors for all books and for the student, compute cosine similarity, sort, return top 5.
17. **What is in a book profile?** Category, subject, keywords, description and title. Subject and keywords count double.
18. **What is in the student profile?** Interests (weight 3), subjects (weight 2) and previously selected books.
19. **What is the final score?** With history: 0.7 x interest similarity + 0.3 x history similarity. Without history: interest similarity only.
20. **How is student history used?** Selected books are converted to vectors and averaged; books similar to them get a higher score. Rating 4-5 counts double, rating 1-2 is ignored.
21. **What happens for a new student?** No history, so only interests and subjects are used. It still gives recommendations.
22. **What if no book matches?** The API returns an empty list with a friendly message, no crash.
23. **Why remove already-read books?** Recommending a book the student already selected is not useful.
24. **What does Match Score mean?** Cosine similarity x 100. Higher means more similar text. It is not a probability.
25. **Why is the score not 100%?** Interests are a few words and a book has many words, so perfect overlap is rare. The ranking is what matters.
26. **Why did you not use scikit-learn?** To keep Lambda simple and small. I wrote TF-IDF and cosine in pure Python, which also shows I understand the algorithm.
27. **What is the synonym table?** Short forms like AI, ML, DBMS are expanded to full words so they match book descriptions.
28. **How do you avoid random output?** The score is calculated from the text with a formula; the same input always gives the same result.

## C. AWS and cloud
29. **What is cloud computing?** Using computing services (servers, storage, databases) over the internet and paying only for use.
30. **What is AWS?** Amazon Web Services, Amazon's cloud platform.
31. **What is S3?** Simple Storage Service: stores files (objects) in buckets. I use it for the website, images, dataset and model file.
32. **What is DynamoDB?** A fast, serverless NoSQL database from AWS that stores items by key.
33. **Why DynamoDB instead of MySQL?** No server to manage, pay per request, auto scaling, easy with Lambda. My queries are simple key lookups.
34. **What is Lambda?** Runs code without managing servers. It runs only when a request comes, and you pay per use.
35. **What is API Gateway?** The front door that gives a public URL and passes HTTP requests to Lambda.
36. **What is IAM?** Identity and Access Management: controls who can do what. My Lambda has a role with minimum permissions.
37. **Why not put access keys in code?** They can leak. The IAM role gives temporary credentials automatically.
38. **What is serverless?** You write functions; AWS runs, scales and patches the servers for you.
39. **Why serverless for this project?** Low cost, no maintenance, automatic scaling, quick to deploy.
40. **What is a partition key?** The main key that DynamoDB uses to find an item quickly (studentId, bookId, historyId).
41. **What is the GSI you used?** `studentId-index` on ReadingHistory so I can get all books of one student quickly.
42. **What is CloudWatch?** AWS service that stores logs; I use it to debug Lambda.
43. **Why is S3 website HTTP?** S3 hosting supports HTTP only; HTTPS needs CloudFront, which I list as future work.

## D. Web and API
44. **What is a REST API?** A way for programs to talk over HTTP using URLs and methods like GET and POST.
45. **What is JSON?** A simple text format for data: `{"name":"Ravi","year":3}`.
46. **What is CORS?** A browser security rule. The API must say which websites may call it; I enabled it in API Gateway and Lambda.
47. **What HTTP status codes do you use?** 200 OK, 201 created, 400 bad request, 404 not found, 405 wrong method, 500 server error, 503 service unavailable.
48. **How do you handle errors?** Validation on input, try/except around AWS calls, friendly JSON errors, and a final catch-all so Lambda never crashes.

## E. Limits and future
49. **What are the limitations?** Word-based matching only, small demo dataset, no login, HTTP website, no real-time availability.
50. **Future enhancements?** Cognito login, admin panel, collaborative filtering, sentence embeddings, CloudFront HTTPS, book availability and notifications.

## Bonus quick answers
- **Time complexity?** About O(N x V): N books, V words. Fine for thousands of books.
- **How would it scale to 1 lakh books?** Precompute vectors and store them in S3/DynamoDB, and use a vector index.
- **Is the dataset real?** It is demo data created by me; titles and descriptions are original.
- **What is your contribution?** Designed the architecture, wrote the engine, backend, frontend, database, deployment and tests.
