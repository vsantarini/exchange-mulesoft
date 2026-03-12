import json
import requests
import argparse
import sys

def asset_exists(deployment, token, org_id):
 url = (
 f"https://anypoint.mulesoft.com/exchange/api/v2/assets"
 f"/{org_id}/{deployment['assetId']}/{deployment['assetVersion']}"
 )
 r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
 return r.status_code == 200

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--deployment-list", required=True)
 parser.add_argument("--token", required=True)
 parser.add_argument("--org-id", required=True)
 args = parser.parse_args()

 with open(args.deployment_list) as f:
 deployments = json.load(f)
 with open(args.token) as f:
 token = json.load(f)["access_token"]

 missing = []
 for d in deployments:
 if not asset_exists(d, token, args.org_id):
 missing.append(f"{d['assetId']} v{d['assetVersion']}")
 else:
 print(f"✅ Asset found: {d['assetId']} v{d['assetVersion']}")

 if missing:
 print(f"❌ Assets not found on Exchange: {missing}")
 sys.exit(1)