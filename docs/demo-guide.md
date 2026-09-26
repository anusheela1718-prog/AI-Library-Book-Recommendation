# Final-year demo flow (5-7 minutes)

Before the demo: open the website once (warm-up), have the AWS Console tabs ready (DynamoDB, Lambda, CloudWatch), and a backup
local run (`python local_server.py`) in case the internet fails.

| # | Do this | Say this |
|---|---|---|
| 1 | Open the deployed website (S3 URL) | "This is AI Library. The website is hosted on Amazon S3." |
| 2 | Enter Student ID `DEMO01` | "A student identifies with an ID. A new ID is a new student with no history." |
| 3 | Enter name, department BCA, year 3 | "These details are stored in the DynamoDB Students table." |
| 4 | Select interests Machine Learning, Python; subject Artificial Intelligence | "The student tells the system what they like." |
| 5 | Click **Get Recommendations** | "The browser sends a JSON request to API Gateway." |
| 6 | (Optional) show Lambda / CloudWatch tab | "API Gateway calls my Lambda function written in Python." |
| 7 | (Optional) show DynamoDB Books table | "Lambda reads the 108 books from DynamoDB." |
| 8 | Show the result page | "The engine converts books and interests into TF-IDF vectors and finds the highest cosine similarity. These are the top 5 with the match score and the words that matched." |
| 9 | Click **View Details** on one book | "Full details: author, category, subject, keywords, description." |
| 10 | Choose a rating and click **Select Book** | "This selection is stored as reading history in DynamoDB." |
| 11 | Open **Reading History**; show the DynamoDB ReadingHistory item | "Here is the stored history record." |
| 12 | Back to Recommendations -> **Refresh** | "Now the engine also uses history: 70% interests, 30% history. The read book is removed and the ranking changes." |
| 13 | Show an error: empty interests | "Errors are handled with friendly messages." |
| 14 | Show `python -m unittest` (46 tests OK) | "The engine and API are tested." |

Closing line: "It is fully serverless, low cost, simple and can scale by adding more books and better ML later."
