#!/usr/bin/env bash
# Update an ALREADY CREATED deployment after you change code. (Run first-time setup from docs/deployment-guide.md)
#
#   BUCKET=my-bucket bash scripts/deploy.sh backend    # re-deploy Lambda code
#   BUCKET=my-bucket bash scripts/deploy.sh frontend   # re-upload website files
#   BUCKET=my-bucket bash scripts/deploy.sh all
set -e
REGION="${REGION:-ap-south-1}"
FUNCTION="${FUNCTION:-AILibraryBackend}"
: "${BUCKET:?Set BUCKET=your-bucket-name}"
cd "$(dirname "$0")/.."

deploy_backend() {
  python scripts/package_lambda.py
  aws lambda update-function-code --region "$REGION" --function-name "$FUNCTION" --zip-file fileb://build/lambda.zip >/dev/null
  echo "Lambda updated."
}
deploy_frontend() {
  python scripts/upload_to_s3.py --bucket "$BUCKET" --region "$REGION"
}

case "${1:-all}" in
  backend)  deploy_backend ;;
  frontend) deploy_frontend ;;
  all)      deploy_backend; deploy_frontend ;;
  *) echo "Usage: deploy.sh [backend|frontend|all]"; exit 1 ;;
esac
