"""
local_server.py - Run the WHOLE project on your PC (no AWS needed).

    cd backend
    python local_server.py
    open http://localhost:8000

It serves the frontend files and sends API calls to lambda_handler,
using local_store.py instead of DynamoDB. Great for testing and practising the demo.
"""
import json
import os
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

os.environ["USE_LOCAL_STORAGE"] = "true"

import lambda_function  # noqa: E402  (must come after the environment variable)

FRONTEND = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, headers, body):
        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _static(self, path):
        rel = "index.html" if path in ("", "/") else path.lstrip("/")
        full = os.path.normpath(os.path.join(FRONTEND, rel))
        if not full.startswith(FRONTEND) or not os.path.isfile(full):
            return False
        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
        with open(full, "rb") as f:
            self._send(200, {"Content-Type": ctype}, f.read())
        return True

    def _api(self, method):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode("utf-8") if length else None
        query = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        event = {"httpMethod": method, "path": parsed.path, "body": body,
                 "queryStringParameters": query or None}
        result = lambda_function.lambda_handler(event, None)
        self._send(result["statusCode"], result["headers"], result["body"].encode("utf-8"))

    def do_GET(self):
        if not self._static(urlparse(self.path).path):
            self._api("GET")

    def do_POST(self):
        self._api("POST")

    def do_OPTIONS(self):
        self._api("OPTIONS")

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.command, self.path))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print(f"AI Library running at http://localhost:{port}  (local mode, no AWS)")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
