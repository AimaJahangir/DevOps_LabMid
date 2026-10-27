"""Local report receiver. Saves every POST /report body as test-report.json.
Run: python receiver/receiver.py   (listens on http://localhost:5000)
"""
import json, os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("RECEIVER_PORT", 5000))
OUT = os.environ.get("REPORT_FILE", "test-report.json")
TOKEN = os.environ.get("REPORT_TOKEN", "")


class H(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/report":
            return self._reply(404, {"error": "use POST /report"})
        if TOKEN and self.headers.get("X-Report-Token") != TOKEN:
            return self._reply(401, {"error": "bad token"})
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        except ValueError:
            return self._reply(400, {"error": "invalid JSON"})
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        s = data.get("summary", {})
        print(f"[saved] {OUT}  commit={data.get('commit_sha','')[:7]}  status={s.get('status')}  "
              f"{s.get('passed')}/{s.get('total')} passed")
        self._reply(200, {"saved": OUT})

    def do_GET(self):
        self._reply(200, {"service": "report receiver", "endpoint": "POST /report"})

    def _reply(self, code, body):
        raw = json.dumps(body).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)

    def log_message(self, *a): pass


if __name__ == "__main__":
    print(f"Receiver listening on http://localhost:{PORT}/report  ->  {OUT}")
    HTTPServer(("0.0.0.0", PORT), H).serve_forever()
