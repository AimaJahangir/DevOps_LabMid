# 🎓 AssignHub – Assignment Submission Portal (CSC418 DevOps Midterm)

Zero-dependency portal (Python 3.9+ standard library only) with automated CI testing,
a local JSON report receiver, GitHub Pages deployment and e-mail reports.

## Structure
| Path | Purpose |
|---|---|
| `app/` | Python server, validation, JSON storage |
| `public/index.html` | Beautiful frontend (also the GitHub Pages demo) |
| `tests/test_submissions.py` | 3 required automated tests |
| `scripts/run_tests_and_report.py` | Runs tests, builds report, POSTs it to receiver, exits non-zero on failure |
| `scripts/send_email.py` | Bonus: e-mails the report |
| `receiver/receiver.py` | Local HTTP receiver → saves `test-report.json` |
| `.github/workflows/ci.yml` | CI pipeline (test → email → deploy Pages) |

## Run the application
```bash
python -m app.server        # open http://localhost:8000
```
## Run the tests
```bash
python scripts/run_tests_and_report.py     # or: python -m unittest discover tests -v
```
## Start the local receiver
```bash
python receiver/receiver.py                # http://localhost:5000/report -> test-report.json
```
Local end-to-end check: start the receiver in one terminal, run the tests in another.

## Connect GitHub Actions to your laptop (tunnel)
1. Start receiver: `python receiver/receiver.py`
2. Start tunnel (new terminal): `cloudflared tunnel --url http://localhost:5000`  (or `ngrok http 5000`)
3. Copy the public URL and add repository secret **REPORT_URL** = `https://<your-tunnel>/report`
4. (Optional) add secret **REPORT_TOKEN** and run the receiver with the same `REPORT_TOKEN` env var.

## Secrets (Settings → Secrets and variables → Actions)
`REPORT_URL`, `REPORT_TOKEN` (optional), and for the e-mail bonus `EMAIL_USER`, `EMAIL_PASS` (Gmail App Password), `EMAIL_TO`.
Test update for passing run
## GitHub Pages (bonus)
Settings → Pages → Source: **GitHub Actions**. Deployment runs only on `main` and only if tests pass.
