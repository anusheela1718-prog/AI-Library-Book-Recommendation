# IAM role for Lambda (least privilege)

Role name: `AILibraryLambdaRole`

1. Trust policy: `lambda-trust-policy.json` (lets the Lambda service use the role).
2. Managed policy **AWSLambdaBasicExecutionRole** -> CloudWatch Logs permissions.
3. Inline policy from `lambda-permissions-policy.json` after replacing:
   - `REGION` (e.g. `ap-south-1`)
   - `ACCOUNT_ID` (12-digit number, top-right of AWS Console)
   - `YOUR-BUCKET-NAME`

No administrator access is used. Lambda can only read/write the 3 tables and the `dataset/` and `model/` folders.
