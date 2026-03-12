import requests
import json
import argparse
import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone

SMTP_HOST = os.environ.get("SMTP_HOST", "localhost")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 25))
SMTP_FROM = os.environ.get("SMTP_FROM", "cicd@example.com")

def load_json(path):
 try:
 with open(path) as f:
 return json.load(f)
 except Exception:
 return []

def build_teams_payload(status, apis, env, dry_run, build_info):
 """
 Builds the Microsoft Teams Adaptive Card payload.
 """
 icon = "✅" if status == "success" else "❌"
 color = "00C176" if status == "success" else "D63B3B"
 label = status.upper()
 dry_label = " [DRY RUN]" if dry_run == "true" else ""
 names = ", ".join([a.get("assetId", a.get("name", "N/A")) for a in apis])
 timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

 return {
 "type": "message",
 "attachments": [
 {
 "contentType": "application/vnd.microsoft.card.adaptive",
 "content": {
 "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
 "type": "AdaptiveCard",
 "version": "1.4",
 "body": [
 {
 "type": "TextBlock",
 "text": f"{icon} Exchange CI/CD Pipeline — {label}{dry_label}",
 "weight": "Bolder",
 "size": "Medium",
 "color": "Good" if status == "success" else "Attention"
 },
 {
 "type": "FactSet",
 "facts": [
 {"title": "Environment", "value": env.upper()},
 {"title": "APIs", "value": names},
 {"title": "Build", "value": build_info.get("number", "N/A")},
 {"title": "Triggered by", "value": build_info.get("user", "jenkins")},
 {"title": "Timestamp", "value": timestamp}
 ]
 },
 {
 "type": "ActionSet",
 "actions": [
 {
 "type": "Action.OpenUrl",
 "title": "View Build",
 "url": build_info.get("url", "https://jenkins.example.com")
 }
 ]
 }
 ]
 }
 }
 ]
 }

def notify_teams(webhook_url, payload):
 """
 Sends notification to Microsoft Teams via Incoming Webhook.
 """
 try:
 r = requests.post(
 webhook_url,
 headers={"Content-Type": "application/json"},
 json=payload,
 timeout=15
 )
 r.raise_for_status()
 print("✅ Teams notification sent.")
 except Exception as e:
 print(f"⚠️ Teams notification failed: {e}")

def build_email_body(status, apis, env, dry_run, build_info):
 """
 Builds HTML email body.
 """
 icon = "✅" if status == "success" else "❌"
 color = "#00C176" if status == "success" else "#D63B3B"
 label = status.upper()
 dry_label = " [DRY RUN]" if dry_run == "true" else ""
 timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

 rows = ""
 for a in apis:
 asset_id = a.get("assetId", a.get("name", "N/A"))
 version = a.get("assetVersion", a.get("version", "N/A"))
 gateway = a.get("gatewayName", "N/A")
 rows += f"""
 <tr>
 <td style='padding:6px;border:1px solid #ddd'>{asset_id}</td>
 <td style='padding:6px;border:1px solid #ddd'>{version}</td>
 <td style='padding:6px;border:1px solid #ddd'>{gateway}</td>
 </tr>
 """

 return f"""
 <html>
 <body style='font-family:Arial,sans-serif;color:#333'>
 <h2 style='color:{color}'>{icon} CI/CD Pipeline — {label}{dry_label}</h2>
 <table style='border-collapse:collapse;width:100%'>
 <tr style='background:#f4f4f4'>
 <th style='padding:8px;border:1px solid #ddd;text-align:left'>Asset ID</th>
 <th style='padding:8px;border:1px solid #ddd;text-align:left'>Version</th>
 <th style='padding:8px;border:1px solid #ddd;text-align:left'>Gateway</th>
 </tr>
 {rows}
 </table>
 <br/>
 <table style='border-collapse:collapse'>
 <tr><td style='padding:4px;font-weight:bold'>Environment</td>
 <td style='padding:4px'>{env.upper()}</td></tr>
 <tr><td style='padding:4px;font-weight:bold'>Build</td>
 <td style='padding:4px'>{build_info.get('number', 'N/A')}</td></tr>
 <tr><td style='padding:4px;font-weight:bold'>Triggered by</td>
 <td style='padding:4px'>{build_info.get('user', 'jenkins')}</td></tr>
 <tr><td style='padding:4px;font-weight:bold'>Timestamp</td>
 <td style='padding:4px'>{timestamp}</td></tr>
 <tr><td style='padding:4px;font-weight:bold'>Build URL</td>
 <td style='padding:4px'>
 <a href='{build_info.get('url', '#')}'>View Build</a>
 </td></tr>
 </table>
 </body>
 </html>
 """

def notify_email(to_addresses, subject, html_body):
 """
 Sends HTML email notification via SMTP.
 """
 try:
 msg = MIMEMultipart("alternative")
 msg["Subject"] = subject
 msg["From"] = SMTP_FROM
 msg["To"] = ", ".join(to_addresses)
 msg.attach(MIMEText(html_body, "html"))

 with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
 server.ehlo()
 server.sendmail(SMTP_FROM, to_addresses, msg.as_string())

 print(f"✅ Email notification sent to: {', '.join(to_addresses)}")

 except Exception as e:
 print(f"⚠️ Email notification failed: {e}")

if __name__ == "__main__":
 parser = argparse.ArgumentParser(
 description="Send CI/CD pipeline notifications via Teams and Email."
 )
 parser.add_argument("--api-list", required=True, help="Path to deployment or API list JSON")
 parser.add_argument("--teams-webhook", required=True, help="Microsoft Teams incoming webhook URL")
 parser.add_argument("--email", required=True, help="Comma-separated list of recipient email addresses")
 parser.add_argument("--status", required=True, choices=["success", "failure"], help="Pipeline status")
 parser.add_argument("--env", default="dev", help="Target environment (dev/test/prod)")
 parser.add_argument("--dry-run", default="false", help="Whether this was a dry-run execution")
 args = parser.parse_args()

 apis = load_json(args.api_list)
 recipients = [e.strip() for e in args.email.split(",") if e.strip()]

 build_info = {
 "number": os.environ.get("BUILD_NUMBER", "N/A"),
 "url": os.environ.get("BUILD_URL", "https://jenkins.example.com"),
 "user": os.environ.get("BUILD_USER", "jenkins")
 }

 icon = "✅" if args.status == "success" else "❌"
 dry_label = " [DRY RUN]" if args.dry_run == "true" else ""
 subject = f"{icon} [CI/CD] Pipeline {args.status.upper()}{dry_label} — {args.env.upper()}"

 print(f"📢 Sending notifications — Status: {args.status.upper()} | Env: {args.env.upper()}")

 # Teams
 teams_payload = build_teams_payload(
 args.status, apis, args.env,
 args.dry_run, build_info
 )
 notify_teams(args.teams_webhook, teams_payload)

 # Email
 html_body = build_email_body(
 args.status, apis, args.env,
 args.dry_run, build_info
 )
 notify_email(recipients, subject, html_body)

 print("✅ All notifications dispatched.")