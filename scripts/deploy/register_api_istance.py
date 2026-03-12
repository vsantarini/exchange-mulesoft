import json
import requests
import argparse

BASE_URL = "https://anypoint.mulesoft.com/apimanager/api/v1/organizations"

def get_existing_instances(org_id, env_id, token):
 url = f"{BASE_URL}/{org_id}/environments/{env_id}/apis"
 r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
 r.raise_for_status()
 return r.json().get("assets", [])

def register_instance(deployment, token, org_id):
 env_id = deployment["environmentId"]
 url = f"{BASE_URL}/{org_id}/environments/{env_id}/apis"

 payload = {
 "spec": {
 "assetId": deployment["assetId"],
 "groupId": deployment.get("groupId", org_id),
 "version": deployment["assetVersion"]
 },
 "endpoint": {
 "uri": deployment["endpointUri"],
 "proxyUri": deployment.get("proxyUri", ""),
 "isCloudHub": False,
 "deploymentType": "HY"
 },
 "instanceLabel": deployment.get("instanceLabel", deployment["assetId"]),
 "technology": "flexGateway"
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
 result = r.json()
 print(f"✅ API Instance registered: {result['id']} for {deployment['assetId']}")
 return result

def update_instance(instance_id, deployment, token, org_id):
 env_id = deployment["environmentId"]
 url = f"{BASE_URL}/{org_id}/environments/{env_id}/apis/{instance_id}"
 payload = {
 "endpoint": {
 "uri": deployment["endpointUri"],
 "proxyUri": deployment.get("proxyUri", "")
 },
 "instanceLabel": deployment.get("instanceLabel", deployment["assetId"])
 }
 r = requests.patch(
 url,
 headers={
 "Authorization": f"Bearer {token}",
 "Content-Type": "application/json"
 },
 json=payload
 )
 r.raise_for_status()
 print(f"✅ API Instance updated: {instance_id}")
 return {"id": instance_id}

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--deployment-list", required=True)
 parser.add_argument("--token", required=True)
 parser.add_argument("--org-id", required=True)
 parser.add_argument("--output", required=True)
 args = parser.parse_args()

 with open(args.deployment_list) as f:
 deployments = json.load(f)
 with open(args.token) as f:
 token = json.load(f)["access_token"]

 api_instances = {}
 for d in deployments:
 existing = get_existing_instances(args.org_id, d["environmentId"], token)
 match = next(
 (i for i in existing if i.get("assetId") == d["assetId"]),
 None
 )
 if match:
 result = update_instance(match["id"], d, token, args.org_id)
 else:
 result = register_instance(d, token, args.org_id)

 api_instances[d["assetId"]] = {
 "instanceId": result["id"],
 "environmentId": d["environmentId"],
 "gatewayName": d["gatewayName"]
 }

 with open(args.output, "w") as f:
 json.dump(api_instances, f, indent=2)
 print("✅ API instances saved.")