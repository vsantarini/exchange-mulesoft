import json
import requests
import argparse

BASE_URL = "https://anypoint.mulesoft.com/apimanager/api/v1/organizations"

def get_gateway_id(org_id, env_id, gateway_name, token):
 url = (
 f"https://anypoint.mulesoft.com/apimanager/api/v1/organizations"
 f"/{org_id}/environments/{env_id}/flexGateway/targets"
 )
 r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
 r.raise_for_status()
 for gw in r.json().get("targets", []):
 if gw["name"] == gateway_name:
 return gw["id"]
 raise ValueError(f"Gateway '{gateway_name}' not found.")

def deploy_to_gateway(instance_info, gateway_id, token, org_id):
 env_id = instance_info["environmentId"]
 instance_id = instance_info["instanceId"]
 url = (
 f"{BASE_URL}/{org_id}/environments/{env_id}"
 f"/apis/{instance_id}/deployments"
 )
 payload = {
 "type": "HY",
 "gatewayVersion": "latest",
 "targetId": gateway_id,
 "overwrite": True
 }
 r = requests.post(
 url,
 headers={
 "Authorization": f"Bearer {token}",
 "Content-Type": "application/json"
 },
 json=payload
 )
 r.raise_for_status()
 print(f"✅ Deployed instance {instance_id} to gateway {gateway_id}")

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--deployment-list", required=True)
 parser.add_argument("--api-instances", required=True)
 parser.add_argument("--token", required=True)
 parser.add_argument("--org-id", required=True)
 args = parser.parse_args()

 with open(args.deployment_list) as f:
 deployments = json.load(f)
 with open(args.api_instances) as f:
 api_instances = json.load(f)
 with open(args.token) as f:
 token = json.load(f)["access_token"]

 for d in deployments:
 instance_info = api_instances.get(d["assetId"])
 if not instance_info:
 print(f"⚠️ No instance found for {d['assetId']}, skipping.")
 continue

 gateway_id = get_gateway_id(
 args.org_id,
 d["environmentId"],
 d["gatewayName"],
 token
 )
 deploy_to_gateway(instance_info, gateway_id, token, args.org_id)