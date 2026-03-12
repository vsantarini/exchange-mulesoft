import json
import requests
import argparse
import sys

def get_gateways(org_id, env_id, token):
 url = (
 f"https://anypoint.mulesoft.com/apimanager/api/v1/organizations"
 f"/{org_id}/environments/{env_id}/flexGateway/targets"
 )
 r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
 r.raise_for_status()
 return {gw["name"]: gw for gw in r.json().get("targets", [])}

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

 errors = []
 for d in deployments:
 gateways = get_gateways(args.org_id, d["environmentId"], token)
 if d["gatewayName"] not in gateways:
 errors.append(f"{d['gatewayName']} not found in env {d['environmentId']}")
 else:
 gw = gateways[d["gatewayName"]]
 print(f"✅ Gateway found: {d['gatewayName']} (status: {gw.get('status')})")

 if errors:
 for e in errors:
 print(f"❌ {e}")
 sys.exit(1)