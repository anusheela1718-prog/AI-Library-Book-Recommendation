# Database design (Amazon DynamoDB)

DynamoDB is a key-value / document database. You always find an item by its **partition key**. Capacity mode: **On-demand**.

## Table 1: Students
| Attribute | Type | Note |
|---|---|---|
| **studentId** | String | **Partition key** (e.g. ST001) |
| name | String | |
| department | String | e.g. BCA |
| year | String | 1-4 |
| interests | List of String | e.g. ["Java","AI"] |
| subjects | List of String | e.g. ["Programming"] |

## Table 2: Books
| Attribute | Type | Note |
|---|---|---|
| **bookId** | String | **Partition key** (B001...) |
| title, author, category, subject | String | |
| keywords | String | comma separated |
| description | String | used for TF-IDF |
| imageUrl | String | e.g. `images/B001.svg` (file is in S3 `images/`) |

## Table 3: ReadingHistory
| Attribute | Type | Note |
|---|---|---|
| **historyId** | String | **Partition key** (unique id created by Lambda) |
| studentId | String | GSI partition key |
| bookId | String | |
| selectedAt | String | ISO time, GSI sort key |
| rating | Number | optional 1-5 |

**GSI `studentId-index`** (partition `studentId`, sort `selectedAt`, projection ALL): lets us get "all books of one student,
newest first" with a fast Query instead of scanning the whole table.

## Why DynamoDB and not MySQL?
Serverless (no server to run), pay per request, scales automatically, integrates with Lambda through IAM,
and our access patterns are simple key lookups. MySQL/RDS needs a running server (cost, patching, connections).

## Create the tables
Console steps: `docs/deployment-guide.md` STEP 5. CLI: `aws/dynamodb/create-tables.sh`.
Load sample data: `python scripts/seed_dynamodb.py --region ap-south-1`.

## Access patterns
| Need | Operation |
|---|---|
| All books (for recommendation) | Scan Books (108 items, cached 5 minutes) |
| One book / one student | GetItem |
| Save student / selection | PutItem |
| History of a student | Query on `studentId-index` |
