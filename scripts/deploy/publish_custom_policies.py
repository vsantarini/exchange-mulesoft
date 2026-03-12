import json
import requests
import argparse
import os
import sys

BASE_EXCHANGE = "https://anypoint.mulesoft.com/exchange/api/v2/assets"

def get_existing_versions(org_id, asset_id, token):
 """
 Recupera tutte le versioni esistenti della policy su Exchange.
 """
 url = f"{BASE_EXCHANGE}/{org_id}/{asset_id}"
 r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
 if r.status_code == 404:
 return []
 r.raise_for_status()
 return [v["version"] for v in r.json().get("instances", [])]

def policy_version_exists(org_id, asset_id, version, token):
 """
 Verifica se una specifica versione esiste su Exchange.
 """
 url = f"{BASE_EXCHANGE}/{org_id}/{asset_id}/{version}"
 r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
 return r.status_code == 200

def publish_custom_policy(policy, org_id, token, dry_run):
 asset_id = policy["customPolicyAssetId"]
 version = policy["customPolicyVersion"]
 name = policy.get("customPolicyName", asset_id)
 jar_path = policy["customPolicyJarPath"]
 yaml_path = policy["customPolicyYamlPath"]

 if not os.path.exists(jar_path):
 print(f"❌ JAR file not found: {jar_path}")
 sys.exit(1)
 if not os.path.exists(yaml_path):
 print(f"❌ YAML descriptor not found: {yaml_path}")
 sys.exit(1)

 if dry_run:
 print(f"[DRY RUN] Would publish custom policy: {asset_id} v{version}")
 return

 print(f"📦 Publishing custom policy: {asset_id} v{version}")

 with open(jar_path, "rb") as jar_f, open(yaml_path, "rb") as yaml_f:
 r = requests.post(
 BASE_EXCHANGE,
 headers={"Authorization": f"Bearer {token}"},
 data={
 "organizationId": org_id,
 "groupId": org_id,
 "assetId": asset_id,
 "version": version,
 "name": name,
 "classifier": "policy",
 "apiVersion": policy.get("customPolicyApiVersion", "v1"),
 "main": os.path.basename(yaml_path)
 },
 files=[
 ("file", (os.path.basename(jar_path), jar_f, "application/java-archive")),
 ("file.yaml", (os.path.basename(yaml_path), yaml_f, "application/yaml"))
 ]
 )

 if r.status_code in (200, 201):
 print(f"✅ Custom policy published: {asset_id} v{version}")
 elif r.status_code == 409:
 print(f"✅ Custom policy already exists: {asset_id} v{version}")
 else:
 print(f"❌ Failed to publish {asset_id}: {r.status_code} — {r.text}")
 sys.exit(1)

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--policy-list", required=True)
 parser.add_argument("--token", required=True)
 parser.add_argument("--org-id", required=True)
 parser.add_argument("--dry-run", default="false")
 args = parser.parse_args()

 with open(args.policy_list) as f:
 policies = json.load(f)
 with open(args.token) as f:
 token = json.load(f)["access_token"]

 dry_run = args.dry_run == "true"
 custom_policies = [p for p in policies if p.get("policyType") == "custom"]

 if not custom_policies:
 print("✅ No custom policies to process.")
 sys.exit(0)

 published = set()
 for policy in custom_policies:
 asset_id = policy["customPolicyAssetId"]
 version = policy["customPolicyVersion"]
 key = f"{asset_id}:{version}"

 if key in published:
 print(f"⏭️ Already processed in this run: {key}")
 continue

 print(f"\n🔍 Checking custom policy: {asset_id} v{version}")

 # Recupera tutte le versioni esistenti
 existing_versions = get_existing_versions(args.org_id, asset_id, token)

 if existing_versions:
 print(f" ├── Versions on Exchange: {existing_versions}")

 if version in existing_versions:
 # Versione esatta già presente — skip
 print(f" └── ✅ Version {version} already exists — skipping publication.")
 else:
 # Asset esiste ma versione diversa — pubblica nuova versione
 print(f" └── ⚠️ Version {version} not found — publishing new version...")
 if policy.get("customPolicyJarPath") and policy.get("customPolicyYamlPath"):
 publish_custom_policy(policy, args.org_id, token, dry_run)
 else:
 print(f" └── ❌ No local files defined for {asset_id} v{version} — cannot publish.")
 sys.exit(1)
 else:
 # Asset non esiste — prima pubblicazione
 print(f" └── 📦 Asset not found — first publication...")
 if policy.get("customPolicyJarPath") and policy.get("customPolicyYamlPath"):
 publish_custom_policy(policy, args.org_id, token, dry_run)
 else:
 print(f" └── ❌ No local files defined for {asset_id} — cannot publish.")
 sys.exit(1)

 published.add(key)

 print("\n✅ Custom policy publication completed.")