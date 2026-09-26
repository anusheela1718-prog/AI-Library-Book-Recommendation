#!/usr/bin/env bash
# Creates an HTTP API in front of the Lambda function (with CORS). Run in Git Bash / Linux / macOS / CloudShell.
#   REGION=ap-south-1 FUNCTION=AILibraryBackend bash aws/api-gateway/create-api.sh
set -e
REGION="${REGION:-ap-south-1}"
FUNCTION="${FUNCTION:-AILibraryBackend}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
LAMBDA_ARN="arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:${FUNCTION}"

# "Quick create": makes the API, the Lambda integration, a $default route and an auto-deployed $default stage.
API_ID=$(aws apigatewayv2 create-api --region "$REGION" --name ai-library-api \
  --protocol-type HTTP --target "$LAMBDA_ARN" \
  --cors-configuration '{"AllowOrigins":["*"],"AllowMethods":["GET","POST","OPTIONS"],"AllowHeaders":["Content-Type","Authorization"],"MaxAge":3600}' \
  --query ApiId --output text)

# Allow API Gateway to call the Lambda function
aws lambda add-permission --region "$REGION" --function-name "$FUNCTION" \
  --statement-id apigateway-invoke --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/*"

echo
echo "YOUR API URL (paste into frontend/js/config.js):"
echo "https://${API_ID}.execute-api.${REGION}.amazonaws.com"
