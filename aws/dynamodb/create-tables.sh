#!/usr/bin/env bash
# Creates the 3 DynamoDB tables. Run in Git Bash / Linux / macOS / AWS CloudShell.
#   REGION=ap-south-1 bash aws/dynamodb/create-tables.sh
set -e
REGION="${REGION:-ap-south-1}"          # <-- change if you use another region

aws dynamodb create-table --region "$REGION" --table-name Students \
  --attribute-definitions AttributeName=studentId,AttributeType=S \
  --key-schema AttributeName=studentId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

aws dynamodb create-table --region "$REGION" --table-name Books \
  --attribute-definitions AttributeName=bookId,AttributeType=S \
  --key-schema AttributeName=bookId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# ReadingHistory: partition key historyId + index to find all books of one student
aws dynamodb create-table --region "$REGION" --table-name ReadingHistory \
  --attribute-definitions AttributeName=historyId,AttributeType=S \
                          AttributeName=studentId,AttributeType=S \
                          AttributeName=selectedAt,AttributeType=S \
  --key-schema AttributeName=historyId,KeyType=HASH \
  --global-secondary-indexes '[{"IndexName":"studentId-index","KeySchema":[{"AttributeName":"studentId","KeyType":"HASH"},{"AttributeName":"selectedAt","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}}]' \
  --billing-mode PAY_PER_REQUEST

echo "Tables are being created. Check status with:  aws dynamodb list-tables --region $REGION"
