"""Tiny JSON-file storage for submissions."""
import json, os, threading
from datetime import datetime, timezone
from .validation import validate


class SubmissionStore:
    def __init__(self, path="data/submissions.json"):
        self.path = path
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        if not os.path.exists(path):
            self._write([])

    def _write(self, items):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2)

    def list(self):
        with self._lock, open(self.path, encoding="utf-8") as f:
            return json.load(f)

    def add(self, data):
        """Returns (record, errors). Invalid input is never saved."""
        errors = validate(data)
        if errors:
            return None, errors
        with self._lock:
            with open(self.path, encoding="utf-8") as f:
                items = json.load(f)
            record = {
                "id": len(items) + 1,
                "name": data["name"].strip(),
                "reg_no": data["reg_no"].strip(),
                "title": data["title"].strip(),
                "url": data["url"].strip(),
                "submitted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            items.append(record)
            self._write(items)
        return record, {}
