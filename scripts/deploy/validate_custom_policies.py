import json
import requests
import argparse
import sys

BASE_EXCHANGE = "https://anypoint.mulesoft.com/exchange/api/v2/assets"

def policy_exists_on_exchange(org_id, asset_id, version, token):
 url = f"{BASE_EXCHANGE}/{org_id}/{asset_id}/{version}"
 r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
 return r.status_code == 200

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

 # Filtra solo le custom policy
 custom_policies = [
 p for p in policies
 if p.get("policyType") == "custom"
 ]

 if not custom_policies:
 print("✅ No custom policies to validate.")
 sys.exit(0)

 missing = []
 to_publish = []

 for p in custom_policies:
 asset_id = p["customPolicyAssetId"]
 version = p["customPolicyVersion"]

 print(f"🔍 Checking custom policy on Exchange: {asset_id} v{version}")

 if policy_exists_on_exchange(args.org_id, asset_id, version, token):
 print(f" └── ✅ Found on Exchange: {asset_id} v{version}")
 else:
 # Verifica se esiste il file locale per la pubblicazione
 if p.get("customPolicyJarPath") and p.get("customPolicyYamlPath"):
 print(f" └── ⚠️ Not found on Exchange — will be published: {asset_id}")
 to_publish.append(asset_id)
 else:
 print(f" └── ❌ Not found and no local files defined: {asset_id}")
 missing.append(asset_id)

 if missing:
 print(f"\n❌ Custom policies missing and cannot be published: {missing}")
 if args.dry_run != "true":
 sys.exit(1)
 else:
 print("⚠️ DRY RUN — blocking errors found but not stopping.")

 if to_publish:
 print(f"\n📦 Custom policies to be published: {to_publish}")

 print("\n✅ Custom policy validation completed.")