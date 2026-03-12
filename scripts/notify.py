import json
import requests
import argparse
import smtplib
from email.mime.text import MIMEText

def notify_teams(webhook_url, message):
 requests.post(
 webhook_url,
 json={"text": message}
 )

def notify_email(to, subject, body):
 msg = MIMEText(body)
 msg["Subject"] = subject
 msg["From"] = "cicd@example.com"
 msg["To"] = to
 with smtplib.SMTP("localhost") as s:
 s.send_message(msg)

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--api-list", required=True)
 parser.add_argument("--teams-webhook", required=True)
 parser.add_argument("--email", required=True)
 parser.add_argument("--status", required=True, choices=["success", "failure"])
 args = parser.parse_args()

 with open(args.api_list) as f:
 apis = json.load(f)

 names = ", ".join([a["name"] for a in apis])
 icon = "✅" if args.status == "success" else "❌"
 msg = (
 f"{icon} Exchange CI/CD Pipeline — {args.status.upper()}\n"
 f"APIs processed: {names}"
 )

 notify_teams(args.teams_webhook, msg)
 notify_email(
 args.email,
 f"[Exchange CI/CD] Pipeline {args.status.upper()}",
 msg
 )
 print(f"✅ Notifications sent.")