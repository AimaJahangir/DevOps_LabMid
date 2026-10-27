"""Run the tests, build a JSON report, POST it to the local receiver, exit non-zero on failure."""
import json, os, sys, unittest, urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class Collector(unittest.TextTestResult):
    def __init__(self, *a, **k):
        super().__init__(*a, **k); self.records = []

    def _add(self, test, result, msg=None):
        self.records.append({"name": test.id().split(".", 1)[-1], "result": result, "failure_message": msg})

    def addSuccess(self, t): super().addSuccess(t); self._add(t, "passed")
    def addFailure(self, t, e): super().addFailure(t, e); self._add(t, "failed", self._exc_info_to_string(e, t))
    def addError(self, t, e): super().addError(t, e); self._add(t, "failed", self._exc_info_to_string(e, t))


def main():
    suite = unittest.defaultTestLoader.discover("tests")
    runner = unittest.TextTestRunner(verbosity=2, resultclass=Collector)
    res = runner.run(suite)
    failed = sum(1 for r in res.records if r["result"] == "failed")
    report = {
        "repository": os.environ.get("GITHUB_REPOSITORY", "local/submission-portal"),
        "branch": os.environ.get("GITHUB_REF_NAME", "local"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local"),
        "pipeline_run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tests": res.records,
        "summary": {"total": len(res.records), "passed": len(res.records) - failed,
                    "failed": failed, "status": "PASSED" if failed == 0 else "FAILED"},
    }
    with open("test-report.json", "w") as f:
        json.dump(report, f, indent=2)

    url = os.environ.get("REPORT_URL") or "http://localhost:5000/report"
    try:
        req = urllib.request.Request(url, json.dumps(report).encode(), {
            "Content-Type": "application/json", "X-Report-Token": os.environ.get("REPORT_TOKEN", "")})
        with urllib.request.urlopen(req, timeout=20) as r:
            print(f"Report delivered to {url} (HTTP {r.status})")
    except Exception as e:  # delivery problems must not hide test results
        print(f"WARNING: could not deliver report to {url}: {e}")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
