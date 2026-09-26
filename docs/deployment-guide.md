# Deployment guide (beginner friendly)

Time needed: about 2-3 hours the first time. **Practise locally first** (README section 13) so you know the app works.

## Values you must choose and replace everywhere
| Placeholder | Example | Where it appears |
|---|---|---|
| `REGION` | `ap-south-1` (Mumbai) | Console top-right region selector, CLI commands, IAM policy |
| `YOUR-BUCKET-NAME` | `ailibrary-yourname-2026` | S3, IAM policy, bucket policy, Lambda env variable |
| `ACCOUNT_ID` | `123456789012` | IAM policy (click your name top-right to see it) |
| Table names | `Students`, `Books`, `ReadingHistory` | Keep these names and you change nothing |
| API URL | `https://abc123.execute-api.ap-south-1.amazonaws.com` | `frontend/js/config.js` |

**Use ONE region for everything** (this guide uses `ap-south-1`). Most "it does not work" problems are a region mismatch.
Windows users: run the shell (`bash`) commands in **Git Bash**, or use the Console clicks instead. Python commands work everywhere.

---
## STEP 1 - Create the AWS account
1. **CLICK HERE:** https://aws.amazon.com -> **Create an AWS Account**.
2. **ENTER THIS VALUE:** your email, account name `AI Library`, password. Add a debit/credit card (needed for verification; this project costs ~0 within the free tier).
3. **SELECT THIS:** Support plan **Basic (free)**.
4. Sign in to the **AWS Management Console** as root, then **SELECT THIS:** region **Asia Pacific (Mumbai) ap-south-1** at the top-right.
5. Safety: on the root account **CLICK HERE:** name (top-right) -> Security credentials -> enable MFA.

## STEP 2 - Configure the AWS CLI
1. Install AWS CLI v2: https://aws.amazon.com/cli/ . Check: `aws --version`. Install Python 3.9+ and run `pip install boto3`.
2. Create a user for the CLI (do NOT use root keys): Console -> **IAM** -> **Users** -> **Create user** ->
   **ENTER THIS VALUE:** `ailibrary-deployer` -> Next -> **SELECT THIS:** *Attach policies directly* -> tick **AdministratorAccess** (only for this setup; delete the user/keys after your project is submitted) -> Create user.
3. Open the user -> **Security credentials** -> **Create access key** -> use case **Command Line Interface (CLI)** -> Create -> keep the page open.
4. In a terminal:
```bash
aws configure
# AWS Access Key ID:      <paste the key>        (never put it in project files or GitHub!)
# AWS Secret Access Key:  <paste the secret>
# Default region name:    ap-south-1
# Default output format:  json
aws sts get-caller-identity      # must print your Account number
```

## STEP 3 - Create the S3 bucket
Console: **S3** -> **CLICK HERE:** *Create bucket*
- Bucket name: **ENTER THIS VALUE:** `ailibrary-yourname-2026` (must be globally unique, lowercase)
- Region: **SELECT THIS:** Asia Pacific (Mumbai) ap-south-1
- Block Public Access: **untick "Block all public access"** and tick the warning "I acknowledge..." (needed for the website; private folders stay private through the policy)
- Leave everything else -> **Create bucket**.

CLI alternative:
```bash
BUCKET=ailibrary-yourname-2026
REGION=ap-south-1
aws s3api create-bucket --bucket $BUCKET --region $REGION --create-bucket-configuration LocationConstraint=$REGION
aws s3api put-public-access-block --bucket $BUCKET --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false
```
(For `us-east-1` leave out the `--create-bucket-configuration` part.)

## STEP 4 - Upload the dataset
```bash
aws s3 cp dataset/books.csv s3://$BUCKET/dataset/books.csv
```
Or Console: open the bucket -> **Create folder** `dataset` -> open it -> **Upload** -> `dataset/books.csv`.
(The website files and images are uploaded in STEP 13.)

## STEP 5 - Create the DynamoDB tables
Console: **DynamoDB** -> **Tables** -> **CLICK HERE:** *Create table* (three times):

| # | Table name (ENTER THIS VALUE) | Partition key | Extra |
|---|---|---|---|
| 1 | `Students` | `studentId` - String | |
| 2 | `Books` | `bookId` - String | |
| 3 | `ReadingHistory` | `historyId` - String | after creation add the index below |

For each: **Table settings** -> **SELECT THIS:** *Customize settings* -> **Capacity mode: On-demand** -> Create table.

Index for ReadingHistory: open the table -> tab **Indexes** -> **Create index** ->
Partition key **ENTER THIS VALUE:** `studentId` (String) - Sort key: `selectedAt` (String) - Index name: `studentId-index` - Attribute projections: **All** -> Create index. Wait until status is **Active**.

CLI alternative (creates all three): `REGION=ap-south-1 bash aws/dynamodb/create-tables.sh`

**Load the sample data (108 books, 10 students, history):**
```bash
python scripts/seed_dynamodb.py --region ap-south-1
```
Check: DynamoDB -> Tables -> Books -> **Explore table items** shows 108 items.

## STEP 6 - Create the IAM role for Lambda
1. **IAM** -> **Roles** -> **CLICK HERE:** *Create role*.
2. Trusted entity: **SELECT THIS:** *AWS service* -> Use case **Lambda** -> Next.
3. Add permission: search and tick **AWSLambdaBasicExecutionRole** (this allows CloudWatch logs) -> Next.
4. Role name: **ENTER THIS VALUE:** `AILibraryLambdaRole` -> **Create role**.
5. Open the new role -> **Permissions** tab -> **Add permissions** -> **Create inline policy** -> **JSON** tab.
   Paste the content of `aws/iam/lambda-permissions-policy.json` and **replace**
   `REGION` -> `ap-south-1`, `ACCOUNT_ID` -> your 12 digits, `YOUR-BUCKET-NAME` -> your bucket. Next -> name **ENTER THIS VALUE:** `AILibraryDataAccess` -> Create policy.

Minimum permissions given: DynamoDB `GetItem, PutItem, Scan, Query` on the 3 tables + the index; S3 `GetObject, PutObject` on `dataset/*` and `model/*`; CloudWatch Logs (managed policy). Nothing else.

## STEP 7 - Create the Lambda function
**Lambda** -> **CLICK HERE:** *Create function*
- **SELECT THIS:** Author from scratch
- Function name: **ENTER THIS VALUE:** `AILibraryBackend`
- Runtime: **Python 3.12**   Architecture: x86_64
- Permissions -> *Change default execution role* -> **SELECT THIS:** *Use an existing role* -> `AILibraryLambdaRole`
- **Create function**.

## STEP 8 - Package the Lambda code
From the project folder:
```bash
python scripts/package_lambda.py
```
This creates `build/lambda.zip` (about 12 KB). **No dependency installation and no layer are needed** because boto3 is already in Lambda and the TF-IDF engine uses only standard Python.

## STEP 9 - Deploy the code and settings
1. In your function -> tab **Code** -> **Upload from** -> **SELECT THIS:** *.zip file* -> choose `build/lambda.zip` -> Save.
2. **Code** tab -> *Runtime settings* -> **Edit** -> Handler: **ENTER THIS VALUE:** `lambda_function.lambda_handler` -> Save.
3. **Configuration** -> **General configuration** -> Edit -> Memory **256 MB**, Timeout **15 sec** -> Save.
4. **Configuration** -> **Environment variables** -> Edit -> Add:

| Key | Value |
|---|---|
| DYNAMODB_STUDENTS_TABLE | Students |
| DYNAMODB_BOOKS_TABLE | Books |
| DYNAMODB_HISTORY_TABLE | ReadingHistory |
| S3_BUCKET_NAME | your bucket name |

   (Do not add AWS_REGION; Lambda sets it. Do not add any keys.)
5. **Test** tab -> Create new event -> Event name `health` -> Event JSON:
```json
{"rawPath": "/health", "requestContext": {"http": {"method": "GET"}}}
```
   Click **Test**. You should see `"statusCode": 200`. Second test (`recs`):
```json
{"rawPath": "/recommendations", "requestContext": {"http": {"method": "POST"}}, "body": "{\"studentId\":\"ST001\",\"interests\":[\"Java\",\"AI\"],\"subjects\":[\"Programming\"]}"}
```
   You should see 5 books. If not, open **Monitor -> View CloudWatch logs**.

CLI alternative for steps 7-9:
```bash
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
aws lambda create-function --region ap-south-1 --function-name AILibraryBackend --runtime python3.12 \
  --handler lambda_function.lambda_handler --role arn:aws:iam::$ACCOUNT:role/AILibraryLambdaRole \
  --zip-file fileb://build/lambda.zip --timeout 15 --memory-size 256 \
  --environment "Variables={DYNAMODB_STUDENTS_TABLE=Students,DYNAMODB_BOOKS_TABLE=Books,DYNAMODB_HISTORY_TABLE=ReadingHistory,S3_BUCKET_NAME=$BUCKET}"
```
(If the role was created seconds ago, wait 10 seconds and retry.) Later code updates: `bash scripts/deploy.sh backend`.

## STEP 10 - Create API Gateway
**API Gateway** -> **CLICK HERE:** *Create API* -> **HTTP API -> Build**
1. **Integrations** -> *Add integration* -> **Lambda** -> Region `ap-south-1` -> Function **SELECT THIS:** `AILibraryBackend`. API name: **ENTER THIS VALUE:** `ai-library-api` -> Next.
2. **Routes**: edit the default route: Method **ANY**, Resource path **ENTER THIS VALUE:** `/{proxy+}` , Integration target `AILibraryBackend` -> Next.
3. **Stages**: keep `$default` with *Auto-deploy* ON -> Next -> **Create**.
4. Copy the **Invoke URL** shown on the API page, like `https://abc123xyz.execute-api.ap-south-1.amazonaws.com`. **This is your API URL.**
5. Test in a browser: `YOUR-API-URL/health` -> you should see `{"status": "ok", ...}`.

CLI alternative (does steps 10 and 11 together): `REGION=ap-south-1 bash aws/api-gateway/create-api.sh` (prints the URL).

## STEP 11 - Enable CORS
CORS lets the website (on the S3 domain) call the API (on the API Gateway domain). Without it the browser blocks requests.
API Gateway -> your API -> left menu **CORS** -> **Configure**:
- Access-Control-Allow-Origin: **ENTER THIS VALUE:** `*`  -> Add
- Access-Control-Allow-Headers: **ENTER THIS VALUE:** `content-type`  -> Add
- Access-Control-Allow-Methods: **SELECT THIS:** `GET`, `POST`, `OPTIONS`
- Access-Control-Max-Age: `3600` -> **Save**.

(The Lambda code also returns CORS headers on every response.)

## STEP 12 - Connect the frontend to the API
Open `frontend/js/config.js` and **replace the value**:
```js
window.APP_CONFIG = {
  API_BASE_URL: "https://abc123xyz.execute-api.ap-south-1.amazonaws.com"   // <- YOUR API URL, no slash at the end
};
```
Save the file.

## STEP 13 - Deploy the frontend (S3 static website)
1. Upload everything (website, images, dataset, model file):
```bash
python scripts/upload_to_s3.py --bucket YOUR-BUCKET-NAME --region ap-south-1
```
2. Console -> S3 -> your bucket -> **Properties** tab -> scroll to **Static website hosting** -> **Edit** -> **SELECT THIS:** *Enable* ->
   Index document: **ENTER THIS VALUE:** `index.html`  Error document: `index.html` -> Save changes.
3. **Permissions** tab -> **Bucket policy** -> **Edit** -> paste `aws/s3/bucket-policy.json` after replacing `YOUR-BUCKET-NAME` -> Save changes.
   (Public read is granted only for `*.html`, `css/`, `js/`, `assets/`, `images/`. `dataset/` and `model/` stay private.)
4. **Properties** -> Static website hosting -> copy the **Bucket website endpoint**, like
   `http://ailibrary-yourname-2026.s3-website.ap-south-1.amazonaws.com`. **This is your website URL.**

CLI alternative for step 2-3:
```bash
aws s3 website s3://$BUCKET/ --index-document index.html --error-document index.html
sed "s/YOUR-BUCKET-NAME/$BUCKET/g" aws/s3/bucket-policy.json > /tmp/policy.json
aws s3api put-bucket-policy --bucket $BUCKET --policy file:///tmp/policy.json
```

## STEP 14 - Test the complete application
1. Open the website URL.
2. Enter Student ID `TEST01`, name, pick interests (Java, AI), subject Programming -> **Get Recommendations**.
3. You must see 5 books with match scores.
4. Click **Select Book** on one -> "Saved to your reading history".
5. Open **Reading History** -> the book is listed. In DynamoDB -> `ReadingHistory` -> Explore items -> a new item exists.
6. Go back to Recommendations -> **Refresh Recommendations** -> results change (the read book disappears and similar books rise).
7. Open a book's **View Details**, choose a rating, select it.
8. Try a bad case: leave interests empty -> friendly error message.

Full checklist: `docs/testing.md`. Demo script: `docs/demo-guide.md`.

---
## Common errors and fixes
| Error | Reason | Fix |
|---|---|---|
| "Cannot reach the server..." on the page | `config.js` still empty/wrong, or CORS off | Fix URL (no trailing `/`), re-run `upload_to_s3.py`, hard refresh (Ctrl+F5); check STEP 11 |
| API URL shows `{"message":"Not Found"}` | Route not created | STEP 10 route must be `ANY /{proxy+}` (or `$default`) |
| `{"message":"Internal Server Error"}` | Lambda crashed on import or handler wrong | Handler must be `lambda_function.lambda_handler`; ZIP files at root; read CloudWatch |
| `Runtime.ImportModuleError` | You zipped the folder instead of the files | Use `python scripts/package_lambda.py` |
| 503 "database is temporarily unavailable" | IAM policy wrong, wrong region/table names, index not Active | Check policy ARNs (region + account), env variables, GSI status |
| Recommendations empty for every student | Books table empty | Run seed script; check DynamoDB items |
| 403 Forbidden on website | Block Public Access ON or no bucket policy | STEP 3 (untick) and STEP 13 (policy) |
| Images not shown | `images/` not uploaded or policy missing `images/*` | Re-run upload script; check policy |
| `AccessDenied` from AWS CLI | Wrong keys/user | `aws sts get-caller-identity`; re-run `aws configure` |
| `BucketAlreadyExists` | Name taken globally | Use another name |
| Old page after update | Browser cache | Ctrl+F5 |

## Update after changes
`BUCKET=YOUR-BUCKET-NAME bash scripts/deploy.sh all` (or `backend` / `frontend`).

## Clean up (avoid charges after the project)
Delete: API Gateway API, Lambda function, the 3 DynamoDB tables, empty and delete the S3 bucket, IAM role and the `ailibrary-deployer` user (and its access keys).
