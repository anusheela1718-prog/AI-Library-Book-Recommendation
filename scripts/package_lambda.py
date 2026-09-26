"""
package_lambda.py - Builds build/lambda.zip (works on Windows, Mac and Linux).

    python scripts/package_lambda.py

The ZIP contains only the backend .py files. boto3 is already in Lambda, so no extra packages are needed.
"""
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["lambda_function.py", "recommendation_engine.py", "dynamodb_service.py",
         "s3_service.py", "local_store.py", "config.py", "errors.py"]


def main():
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    target = os.path.join(ROOT, "build", "lambda.zip")
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for name in FILES:
            z.write(os.path.join(ROOT, "backend", name), name)   # files must be at the ZIP root
    print(f"Created {target} ({os.path.getsize(target)} bytes)")


if __name__ == "__main__":
    main()
