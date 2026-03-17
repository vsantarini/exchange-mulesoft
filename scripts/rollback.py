import json
import argparse
import requests
import sys

BASE_URL = "https://anypoint.mulesoft.com/exchange/api/v2/assets"

# Mappa step -> funzione di rollback
# Solo gli step che modificano risorse remote hanno un rollback reale

def rollback_publish_assets(api_list, token, org_id):
 print("[INFO] Rolling back published assets...")
 for api in api_list:
     url = f"{BASE_URL}/{org_id}/{api['assetId']}/{api['version']}"
     response = requests.delete(
     url,
     headers={"Authorization": f"Bearer {token}"}
     )
     if response.status_code in (200, 204, 404):
        print(f" [OK] Deleted asset: {api['assetId']} v{api['version']}")
     else:
        print(f" [WARN] Could not delete asset: {api['assetId']} — HTTP {response.status_code}")

def rollback_publish_soap_pages(api_list, token, org_id):
 print("[INFO] Rolling back SOAP pages...")
 for api in api_list:
    if api.get("type") != "soap":
        continue
         url = f"{BASE_URL}/{org_id}/{api['assetId']}/{api['version']}/portal"
         response = requests.delete(
         url,
         headers={"Authorization": f"Bearer {token}"}
         )
    if response.status_code in (200, 204, 404):
        print(f" [OK] Deleted portal pages: {api['assetId']}")
    else:
        print(f" [WARN] Could not delete portal: {api['assetId']} — HTTP {response.status_code}")

def rollback_manage_applications(api_list, token, org_id):
 print("[INFO] Rolling back consumer applications...")
 response = requests.get(
 f"https://anypoint.mulesoft.com/exchange/api/v1/organizations/{org_id}/applications",
 headers={"Authorization": f"Bearer {token}"}
 )
 if response.status_code != 200:
    print(f" [WARN] Could not retrieve applications — HTTP {response.status_code}")
    return
 apps = {app["name"]: app["id"] for app in response.json()}
 for api in api_list:
    app_name = api.get("appName")
    if app_name and app_name in apps:
        del_response = requests.delete(
        f"https://anypoint.mulesoft.com/exchange/api/v1/organizations/{org_id}/applications/{apps[app_name]}",
        headers={"Authorization": f"Bearer {token}"}
        )
    if del_response.status_code in (200, 204, 404):
        print(f" [OK] Deleted application: {app_name}")
    else:
        print(f" [WARN] Could not delete application: {app_name} — HTTP {del_response.status_code}")

# Step che non richiedono rollback remoto
def rollback_noop(step_name):
 print(f"[INFO] No rollback needed for step: {step_name}")

ROLLBACK_MAP = {
 "manage_contracts": lambda apis, token, org_id: rollback_noop("manage_contracts"),
 "manage_applications": rollback_manage_applications,
 "publish_pages": lambda apis, token, org_id: rollback_noop("publish_pages"),
 "update_home_page": lambda apis, token, org_id: rollback_noop("update_home_page"),
 "upload_image": lambda apis, token, org_id: rollback_noop("upload_image"),
 "assign_tags": lambda apis, token, org_id: rollback_noop("assign_tags"),
 "publish_soap_pages": rollback_publish_soap_pages,
 "publish_assets": rollback_publish_assets,
 "generate_docs": lambda apis, token, org_id: rollback_noop("generate_docs"),
 "ensure_categories": lambda apis, token, org_id: rollback_noop("ensure_categories"),
 "check_versions": lambda apis, token, org_id: rollback_noop("check_versions"),
 "validate_specs": lambda apis, token, org_id: rollback_noop("validate_specs"),
 "authenticate": lambda apis, token, org_id: rollback_noop("authenticate"),
 "read_excel": lambda apis, token, org_id: rollback_noop("read_excel"),
}

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--state", required=True)
 parser.add_argument("--token", required=True)
 parser.add_argument("--org-id", required=True)
 parser.add_argument("--api-list", default="api-list.json")
 args = parser.parse_args()

 with open(args.state) as f:
    state = json.load(f)
 with open(args.token) as f:
    token = json.load(f)["access_token"]

 try:
    with open(args.api_list) as f:
        api_list = json.load(f)
 except Exception:
    api_list = []
    print("[WARN] api-list.json not found — rollback will be partial.")

 completed = [s["step"] for s in state.get("completed_steps", [])]
 print(f"[INFO] Rolling back {len(completed)} completed steps in reverse order...")

 for step in reversed(completed):
    print(f"\n[INFO] Rollback: {step}")
    handler = ROLLBACK_MAP.get(step)
    if handler:
        handler(api_list, token, args.org_id)
    else:
        print(f"[WARN] No rollback handler found for step: {step}")

 print("\n[OK] Rollback completed.")