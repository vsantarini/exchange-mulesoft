import json
import requests
import argparse

BASE_URL = "https://anypoint.mulesoft.com/apimanager/api/v1/organizations"

ALERT_CONDITION_MAP = {
 "response-time": "response-time-greater-than",
 "error-rate": "errors-all",
 "request-count": "request-count",
 "policy-violation": "policy-violation"
}

def get_existing_alerts(org_id, env_id, instance_id, token):
 url = f"{BASE_URL}/{org_id}/environments/{env_id}/apis/{instance_id}/alerts"
 r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
 r.raise_for_status()
 return r.json().get("alerts", [])

def create_alert(org_id, env_id, instance_id, alert, token, dry_run):
 if dry_run:
 print(f"[DRY RUN] Would create alert: {alert['alertName']}")
 return

 url = f"{BASE_URL}/{org_id}/environments/{env_id}/apis/{instance_id}/alerts"
 payload = {
 "name": alert["alertName"],
 "enabled": True,
 "severity": alert.get("severity", "WARNING"),
 "condition": {
 "type": ALERT_CONDITION_MAP.get(alert["alertType"], alert["alertType"]),
 "value": int(alert.get("threshold", 1000)),
 "repeat": int(alert.get("repeatCount", 1)),
 "periodInMinutes": int(alert.get("periodMinutes", 5))
 },
 "recipients": [
 {"type": "email", "value": e.strip()}
 for e in alert.get("recipients", "").split(",") if e.strip()
 ]
 }

 r = requests.post(
 url,
 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
 json=payload
 )
 r.raise_for_status()
 print(f"✅ Alert created: {alert['alertName']} for instance {instance_id}")

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--alert-list", required=True)
 parser.add_argument("--api-instances", required=True)
 parser.add_argument("--token", required=True)
 parser.add_argument("--org-id", required=True)
 parser.add_argument("--dry-run", default="false")
 args = parser.parse_args()

 with open(args.alert_list) as f:
 alerts = json.load(f)
 with open(args.api_instances) as f:
 api_instances = json.load(f)
 with open(args.token) as f:
 token = json.load(f)["access_token"]

 dry_run = args.dry_run == "true"

 for alert in alerts:
 asset_id = alert["assetId"]
 instance_info = api_instances.get(asset_id)
 if not instance_info:
 print(f"⚠️ No instance for {asset_id}, skipping alert.")
 continue

 env_id = instance_info["environmentId"]
 instance_id = instance_info["instanceId"]

 existing = get_existing_alerts(args.org_id, env_id, instance_id, token)
 existing_names = [a["name"] for a in existing]

 if alert["alertName"] not in existing_names:
 create_alert(args.org_id, env_id, instance_id, alert, token, dry_run)
 else:
 print(f"✅ Alert already exists: {alert['alertName']}")