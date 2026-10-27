"""Automated tests: the three required cases."""
import json, os, tempfile, threading, unittest, urllib.request, urllib.error
from app.server import create_server
from app.storage import SubmissionStore

VALID = {"name": "Ali Khan", "reg_no": "2021-CS-101",
         "title": "DevOps Lab 1", "url": "https://github.com/ali/devops-lab1"}


class PortalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        store = SubmissionStore(os.path.join(cls.tmp.name, "s.json"))
        cls.server = create_server(0, store)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.tmp.cleanup()

    def post(self, payload):
        req = urllib.request.Request(self.base + "/api/submissions", json.dumps(payload).encode(),
                                     {"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.load(r)
        except urllib.error.HTTPError as e:
            return e.code, json.load(e)

    def listing(self):
        with urllib.request.urlopen(self.base + "/api/submissions") as r:
            return json.load(r)

    def test_valid_submission_is_saved_and_listed(self):
        status, body = self.post(VALID)
        self.assertEqual(status, 201)
        self.assertIn(VALID["reg_no"], [s["reg_no"] for s in self.listing()])

    def test_missing_registration_number_is_rejected(self):
        before = len(self.listing())
        status, body = self.post({**VALID, "reg_no": ""})
        self.assertEqual(status, 422)
        self.assertIn("reg_no", body["errors"])
        self.assertEqual(len(self.listing()), before)

    def test_invalid_url_is_rejected_and_not_saved(self):
        before = len(self.listing())
        status, body = self.post({**VALID, "url": "not-a-url"})
        self.assertEqual(status, 422)
        self.assertIn("url", body["errors"])
        self.assertEqual(len(self.listing()), before)


if __name__ == "__main__":
    unittest.main()
