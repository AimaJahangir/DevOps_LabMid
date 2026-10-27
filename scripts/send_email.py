"""Email the test report (bonus). Credentials come from environment variables / CI secrets."""
import json, os, smtplib
from email.message import EmailMessage

r = json.load(open("test-report.json"))
s = r["summary"]
lines = [f"Repository : {r['repository']}", f"Branch     : {r['branch']}",
         f"Commit     : {r['commit_sha']}", f"Run ID     : {r['pipeline_run_id']}",
         f"Time (UTC) : {r['timestamp']}", f"RESULT     : {s['status']}",
         f"Total {s['total']} | Passed {s['passed']} | Failed {s['failed']}", "", "Individual tests:"]
for t in r["tests"]:
    lines.append(f"  [{t['result'].upper()}] {t['name']}")
    if t["failure_message"]:
        lines.append("      " + t["failure_message"].strip().splitlines()[-1])
m = EmailMessage()
m["Subject"] = f"[{s['status']}] {r['repository']} @ {r['commit_sha'][:7]}"
m["From"], m["To"] = os.environ["EMAIL_USER"], os.environ["EMAIL_TO"]
m.set_content("\n".join(lines))
m.add_attachment(json.dumps(r, indent=2).encode(), maintype="application", subtype="json", filename="test-report.json")
with smtplib.SMTP_SSL(os.environ.get("SMTP_HOST", "smtp.gmail.com"), int(os.environ.get("SMTP_PORT", 465))) as srv:
    srv.login(os.environ["EMAIL_USER"], os.environ["EMAIL_PASS"]); srv.send_message(m)
print("Email sent to", os.environ["EMAIL_TO"])
