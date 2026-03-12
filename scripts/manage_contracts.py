import json
import requests
import argparse

BASE_URL = "https://anypoint.mulesoft.com/exchange/api/v1/organizations"

def get_existing_contracts(org_id, app_id, token):
 response = requests.get(
 f"{BASE_URL}/{org_id}/applications/{app_id}/contracts",
 headers={"Authorization": f"Bearer {token}"}
 )
 response.raise_for_status()
 return response.json()

def create_contract(contract, app_id, org_id, env_id, token):
 payload = {
 "apiId": contract["apiId"],
 "environmentId": env_id,
 "acceptedTerms": True,
 "organizationId": org_id,
 "groupId": contract.get("groupId", org_id),
 "assetId": contract["assetId"],
 "version": contract["version"],
 "versionGroup": contract.get("versionGroup", "v1")
 }
 if contract.get("tierId"):
 payload["tier"] = {"id": contract["tierId"]}

 response = requests.post(
 f"{BASE_URL}/{org_id}/applications/{app_id}/contracts",
 headers={
 "Authorization": f"Bearer {token}",
 "Content-Type": "application/json"
 },
 json=payload
 )
 response.raise_for_status()
 result = response.json()
 print(f"✅ Contract created: app={contract['appName']} → asset={contract['assetId']}")
 return result

def update_contract(contract_id, contract, app_id, org_id, token):
 payload = {"status": contract.get("status", "APPROVED")}
 if contract.get("tierId"):
 payload["tier"] = {"id": contract["tierId"]}

 response = requests.patch(
 f"{BASE_URL}/{org_id}/applications/{app_id}/contracts/{contract_id}",
 headers={
 "Authorization": f"Bearer {token}",
 "Content-Type": "application/json"
 },
 json=payload
 )
 response.raise_for_status()
 print(f"✅ Contract updated: id={contract_id} status={payload['status']}")

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--contract-list", required=True)
 parser.add_argument("--app-ids", required=True)
 parser.add_argument("--token", required=True)
 parser.add_argument("--org-id", required=True)
 parser.add_argument("--env-id", required=True)
 args = parser.parse_args()

 with open(args.contract_list) as f:
 contracts = json.load(f)
 with open(args.app_ids) as f:
 app_ids = json.load(f)
 with open(args.token) as f:
 token = json.load(f)["access_token"]

 for contract in contracts:
 app_name = contract["appName"]
 app_id = app_ids.get(app_name)
 if not app_id:
 print(f"⚠️ App ID not found for: {app_name}, skipping.")
 continue

 existing = get_existing_contracts(args.org_id, app_id, token)
 existing_ids = {
 c["assetId"]: c["id"]
 for c in existing
 if c.get("assetId") == contract["assetId"]
 }

 if contract["assetId"] in existing_ids:
 update_contract(
 existing_ids[contract["assetId"]],
 contract, app_id, args.org_id, token
 )
 else:
 create_contract(contract, app_id, args.org_id, args.env_id, token)