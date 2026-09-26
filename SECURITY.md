# Security Notes

- Do not commit `.env` files, AWS access keys, secret keys, tokens, or passwords.
- This project is designed to use IAM roles on AWS and `aws configure` locally.
- `aws/lambda/environment.json` and `aws/s3/bucket-policy.json` contain placeholders such as `YOUR-BUCKET-NAME`; replace them only in your local/deployment configuration as needed.
- If a real secret is ever committed, revoke/rotate it immediately and remove it from Git history.
