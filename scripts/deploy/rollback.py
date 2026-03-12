import json
import requests
import argparse
import sys

BASE_URL = "https://anypoint.mulesoft.com/apimanager/api/v1/organizations"

def remove_policies(org_id, env_id, instance_id, token, dry_run):
 """Rimuove tutte le policy applicate."""
 url = f"{BASE_URL}/{org_id}/environments/{env_id}/apis/{instance_id}/policies"
 r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
 r.raise_for_status()
 policies = r.json()

 for policy in policies:
 if dry_run:
 print(f"[DRY RUN] Would delete policy: {policy['id']}")
 continue
 del_r = requests.delete(
 f"{url}/{policy['id']}",
 headers={"Authorization": f"Bearer {token}"}
 )
 if del_r.status_code in (200, 204):
 print(f"✅ Policy removed: {policy['id']}")
 else:
 print(f"⚠️ Could not remove policy {policy['id']}: {del_r.status_code}")

def undeploy_instance(org_id, env_id, instance_id, token, dry_run):
 """Rimuove il deployment dell'istanza dal Flex Gateway."""
 if dry_run:
 print(f"[DRY RUN] Would undeploy instance: {instance_id}")
 return

 url = f"{BASE_URL}/{org_id}/environments/{env_id}/apis/{instance_id}/deployments"
 r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
 r.raise_for_status()
 deployments = r.json().get("deployments", [])

 for dep in deployments:
 dep_id = dep["id"]
 del_r = requests.delete(
 f"{url}/{dep_id}",
 headers={"Authorization": f"Bearer {token}"}
 )
 if del_r.status_code in (200, 204):
 print(f"✅ Deployment removed: {dep_id}")

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--api-instances", required=True)
 parser.add_argument("--policy-list", required=True)
 parser.add_argument("--token", required=True)
 parser.add_argument("--org-id", required=True)
 parser.add_argument("--dry-run", default="false")
 args = parser.parse_args()

 with open(args.api_instances) as f:
 api_instances = json.load(f)
 with open(args.token) as f:
 token = json.load(f)["access_token"]

 dry_run = args.dry_run == "true"

 print("🔄 Starting rollback...")
 for asset_id, instance_info in api_instances.items():
 env_id = instance_info["environmentId"]
 instance_id = instance_info["instanceId"]

 print(f"\n🔁 Rolling back: {asset_id}")
 remove_policies(args.org_id, env_id, instance_id, token, dry_run)
 undeploy_instance(args.org_id, env_id, instance_id, token, dry_run)

 print("\n✅ Rollback completed.")