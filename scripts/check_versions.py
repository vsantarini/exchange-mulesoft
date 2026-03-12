import json
import requests
import argparse

def version_exists(api, token, org_id):
 url = (
 f"https://anypoint.mulesoft.com/exchange/api/v2/assets"
 f"/{org_id}/{api['assetId']}/{api['version']}"
 )
 response = requests.get(
 url,
 headers={"Authorization": f"Bearer {token}"}
 )
 return response.status_code == 200

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--api-list", required=True)
 parser.add_argument("--token", required=True)
 parser.add_argument("--org-id", required=True)
 args = parser.parse_args()

 with open(args.api_list) as f:
 apis = json.load(f)
 with open(args.token) as f:
 token = json.load(f)["access_token"]

 conflicts = []
 for api in apis:
 if version_exists(api, token, args.org_id):
 conflicts.append(f"{api['assetId']} v{api['version']}")

 if conflicts:
 print("❌ Version conflicts detected:")
 for c in conflicts:
 print(f" - {c} already exists on Exchange.")
 exit(1)
 else:
 print("✅ No version conflicts detected.")