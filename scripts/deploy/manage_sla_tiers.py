import json
import requests
import argparse

BASE_URL = "https://anypoint.mulesoft.com/apimanager/api/v1/organizations"

def get_existing_tiers(org_id, env_id, instance_id, token):
 url = f"{BASE_URL}/{org_id}/environments/{env_id}/apis/{instance_id}/tiers"
 r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
 r.raise_for_status()
 return {t["name"]: t for t in r.json().get("tiers", [])}

def create_tier(org_id, env_id, instance_id, tier, token, dry_run):
 if dry_run:
 print(f"[DRY RUN] Would create SLA tier: {tier['tierName']}")
 return {"id": f"dry-run-tier-{tier['tierName']}"}

 url = f"{BASE_URL}/{org_id}/environments/{env_id}/apis/{instance_id}/tiers"
 payload = {
 "name": tier["tierName"],
 "description": tier.get("tierDescription", ""),
 "autoApprove": tier.get("autoApprove", "true") == "true",
 "limits": [
 {
 "visible": True,
 "maximumRequests": int(tier["maxRequests"]),
 "timePeriodInMilliseconds": int(tier["timePeriodMs"])
 }
 ]
 }
 r = requests.post(
 url,
 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
 json=payload
 )
 r.raise_for_status()
 result = r.json()
 print(f"✅ SLA Tier created: {tier['tierName']} (id: {result['id']})")
 return result

def update_tier(org_id, env_id, instance_id, tier_id, tier, token, dry_run):
 if dry_run:
 print(f"[DRY RUN] Would update SLA tier: {tier['tierName']}")
 return

 url = f"{BASE_URL}/{org_id}/environments/{env_id}/apis/{instance_id}/tiers/{tier_id}"
 payload = {
 "limits": [
 {
 "visible": True,
 "maximumRequests": int(tier["maxRequests"]),
 "timePeriodInMilliseconds": int(tier["timePeriodMs"])
 }
 ]
 }
 r = requests.patch(
 url,
 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
 json=payload
 )
 r.raise_for_status()
 print(f"✅ SLA Tier updated: {tier['tierName']}")

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--sla-list", required=True)
 parser.add_argument("--deployment-list", required=True)
 parser.add_argument("--token", required=True)
 parser.add_argument("--org-id", required=True)
 parser.add_argument("--dry-run", default="false")
 args = parser.parse_args()

 with open(args.sla_list) as f:
 sla_tiers = json.load(f)
 with open(args.deployment_list) as f:
 deployments = json.load(f)
 with open(args.token) as f:
 token = json.load(f)["access_token"]

 dry_run = args.dry_run == "true"

 # Carica api-instances se disponibile
 try:
 with open("api-instances.json") as f:
 api_instances = json.load(f)
 except FileNotFoundError:
 api_instances = {}

 for tier in sla_tiers:
 asset_id = tier["assetId"]
 instance_info = api_instances.get(asset_id)
 if not instance_info:
 print(f"⚠️ No instance found for {asset_id}, skipping SLA tier.")
 continue

 env_id = instance_info["environmentId"]
 instance_id = instance_info["instanceId"]

 existing = get_existing_tiers(args.org_id, env_id, instance_id, token)

 if tier["tierName"] in existing:
 update_tier(
 args.org_id, env_id, instance_id,
 existing[tier["tierName"]]["id"],
 tier, token, dry_run
 )
 else:
 create_tier(args.org_id, env_id, instance_id, tier, token, dry_run)