"""Submission portal server (Python standard library only).
Run:  python -m app.server   ->  http://localhost:8000
"""
import json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .storage import SubmissionStore

PUBLIC = os.path.join(os.path.dirname(__file__), "..", "public")
TYPES = {".html": "text/html", ".css": "text/css", ".js": "application/javascript"}


def make_handler(store):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, body, ctype="application/json"):
            raw = body if isinstance(body, bytes) else json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype + "; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            if self.path == "/api/submissions":
                return self._send(200, store.list())
            name = "index.html" if self.path in ("/", "") else self.path.lstrip("/").split("?")[0]
            full = os.path.normpath(os.path.join(PUBLIC, name))
            if not full.startswith(os.path.normpath(PUBLIC)) or not os.path.isfile(full):
                return self._send(404, {"error": "Not found"})
            with open(full, "rb") as f:
                self._send(200, f.read(), TYPES.get(os.path.splitext(full)[1], "text/plain"))

        def do_POST(self):
            if self.path != "/api/submissions":
                return self._send(404, {"error": "Not found"})
            try:
                data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            except ValueError:
                return self._send(400, {"errors": {"form": "Invalid JSON."}})
            record, errors = store.add(data)
            if errors:
                return self._send(422, {"errors": errors})
            self._send(201, record)

        def log_message(self, *a):
            pass
    return Handler


def create_server(port=8000, store=None):
    store = store or SubmissionStore(os.environ.get("DATA_FILE", "data/submissions.json"))
    return ThreadingHTTPServer(("0.0.0.0", port), make_handler(store))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Portal running at http://localhost:{port}")
    create_server(port).serve_forever()
