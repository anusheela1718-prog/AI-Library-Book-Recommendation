# DynamoDB tables

| Table | Partition key | Extra index |
|---|---|---|
| Students | `studentId` (String) | - |
| Books | `bookId` (String) | - |
| ReadingHistory | `historyId` (String) | GSI `studentId-index`: partition `studentId` (String), sort `selectedAt` (String) |

Capacity mode: **On-demand** (pay per request, nothing to tune, almost free for a demo).
Run `create-tables.sh`, or follow the Console steps in `docs/deployment-guide.md` (STEP 5).
