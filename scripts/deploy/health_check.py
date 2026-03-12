import json
import requests
import argparse
import sys
import time

def check_api_manager_status(org_id, env_id, instance_id, token, retries=5, delay=10):
 """Verifica stato deploy su API Manager."""
 BASE = "https://anypoint.mulesoft.com/apimanager/api/v1/organizations"
 url = f"{BASE}/{org_id}/environments/{env_id}/apis/{instance_id}/deployments"

 for attempt in range(retries):
 r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
 r.raise_for_status()
 deployments = r.json().get("deployments", [])
 if deployments:
 status = deployments[-1].get("status", "UNKNOWN")
 print(f" ├── Attempt {attempt+1}/{retries} — API Manager Status: {status}")
 if status == "DEPLOYED":
 return True
 elif status in ("FAILED", "UNDEPLOYED"):
 return False
 time.sleep(delay)
 return False

def smoke_test(endpoint_uri, expected_status, headers=None, retries=3, delay=5):
 """Esegue una chiamata HTTP di smoke test sull'endpoint."""
 for attempt in range(retries):
 try:
 r = requests.get(endpoint_uri, headers=headers or {}, timeout=10, verify=False)
 print(f" ├── Smoke test attempt {attempt+1}/{retries} — HTTP {r.status_code}")
 if r.status_code == int(expected_status):
 return True
 except requests.exceptions.RequestException as e:
 print(f" ├── Attempt {attempt+1} failed: {e}")
 time.sleep(delay)
 return False

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

 failed = []
 for d in deployments:
 asset_id = d["assetId"]
 instance_info = api_instances.get(asset_id)
 if not instance_info:
 continue

 print(f"\n🔍 Health check: {asset_id}")

 # Step 1 — API Manager status
 ok = check_api_manager_status(
 args.org_id,
 instance_info["environmentId"],
 instance_info["instanceId"],
 token
 )

 if not ok:
 failed.append(f"{asset_id} — API Manager status not DEPLOYED")
 continue

 # Step 2 — Smoke test sull'endpoint proxy
 proxy_uri = d.get("proxyUri")
 health_path = d.get("healthCheckPath", "/")
 expected = d.get("healthCheckExpectedStatus", "200")

 if proxy_uri:
 full_url = f"{proxy_uri.rstrip('/')}{health_path}"
 smoke_ok = smoke_test(full_url, expected)
 if smoke_ok:
 print(f" └── ✅ Smoke test passed: {full_url}")
 else:
 failed.append(f"{asset_id} — Smoke test failed on {full_url}")
 else:
 print(f" └── ⚠️ No proxyUri defined, skipping smoke test.")

 if failed:
 for f in failed:
 print(f"❌ {f}")
 sys.exit(1)
 else:
 print("\n✅ All health checks passed.")