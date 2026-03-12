import json
import requests
import argparse
import sys

BASE_URL = "https://anypoint.mulesoft.com/apimanager/api/v1/organizations"

# Mappa policy_type → policy template ID
POLICY_ASSET_MAP = {
 "routing": "http-proxy",
 "mtls": "tls-enforcement",
 "request-validation": "request-validation",
 "security": {
 "oauth2": "oauth2-access-token-enforcement",
 "jwt": "jwt-validation",
 "ip-allowlist": "ip-allowlist",
 "ip-blocklist": "ip-blocklist",
 "basic-auth": "http-basic-authentication"
 },
 "rate-limiting": {
 "rate-limit": "rate-limiting",
 "throttling": "throttling",
 "spike-control": "spike-control"
 }
}

def get_existing_policies(org_id, env_id, instance_id, token):
 url = f"{BASE_URL}/{org_id}/environments/{env_id}/apis/{instance_id}/policies"
 r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
 r.raise_for_status()
 return r.json()

def apply_policy(org_id, env_id, instance_id, policy_def, token, dry_run):
 if dry_run:
 print(f"[DRY RUN] Would apply policy: {policy_def.get('policyTemplateId')}")
 return
 url = f"{BASE_URL}/{org_id}/environments/{env_id}/apis/{instance_id}/policies"
 r = requests.post(
 url,
 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
 json=policy_def
 )
 r.raise_for_status()
 print(f" ├── ✅ Policy applied: {policy_def.get('policyTemplateId')}")

def update_policy(org_id, env_id, instance_id, policy_id, policy_def, token, dry_run):
 if dry_run:
 print(f"[DRY RUN] Would update policy: {policy_id}")
 return
 url = f"{BASE_URL}/{org_id}/environments/{env_id}/apis/{instance_id}/policies/{policy_id}"
 r = requests.patch(
 url,
 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
 json={"configurationData": policy_def.get("configurationData", {})}
 )
 r.raise_for_status()
 print(f" ├── 🔄 Policy updated: {policy_id}")

def build_standard_policy_definition(policy, cert_refs):
 """
 Costruisce il payload per le policy standard
 usando POLICY_ASSET_MAP per risolvere il templateId.
 """
 config = {}
 policy_type = policy["policyType"]

 if policy_type == "routing":
 template_id = POLICY_ASSET_MAP["routing"]
 config = {
 "upstreamUri": policy["upstreamUri"],
 "connectTimeout": int(policy.get("connectTimeout", 10000)),
 "readTimeout": int(policy.get("readTimeout", 10000))
 }

 elif policy_type == "mtls":
 template_id = POLICY_ASSET_MAP["mtls"]
 secret_id = cert_refs.get(policy["assetId"], "")
 config = {
 "tlsContextId": secret_id,
 "requireClientCertificate": policy.get("clientCertRequired", "true") == "true",
 "enableMutualAuthentication": True
 }

 elif policy_type == "request-validation":
 template_id = POLICY_ASSET_MAP["request-validation"]
 config = {
 "enableSchemaValidation": policy.get("enableSchemaValidation", "true") == "true",
 "maxRequestSize": int(policy.get("maxRequestSize", 1048576)),
 "allowedMethods": [
 m.strip() for m in policy.get("allowedMethods", "GET,POST,PUT,DELETE").split(",")
 ],
 "requiredHeaders": [
 h.strip() for h in policy.get("requiredHeaders", "").split(",") if h.strip()
 ]
 }

 elif policy_type == "security":
 sub_type = policy.get("securityType", "oauth2")
 template_id = POLICY_ASSET_MAP["security"].get(sub_type, sub_type)
 if sub_type == "jwt":
 config = {
 "jwtExpression": policy.get("jwtExpression", "#[vars.token]"),
 "signingKeyLength": int(policy.get("signingKeyLength", 256)),
 "signingMethod": policy.get("signingMethod", "RSA"),
 "jwksUrl": policy.get("jwksUrl", ""),
 "skipClientIdValidation": policy.get("skipClientIdValidation", "false") == "true"
 }
 elif sub_type == "oauth2":
 config = {
 "tokenUrl": policy["tokenUrl"],
 "scopes": [s.strip() for s in policy.get("scopes", "").split(",") if s.strip()],
 "exposeHeaders": policy.get("exposeHeaders", "false") == "true"
 }
 elif sub_type == "ip-allowlist":
 config = {
 "ipExpression": policy.get("ipExpression", "#[attributes.remoteAddress]"),
 "ips": [ip.strip() for ip in policy.get("allowedIps", "").split(",") if ip.strip()]
 }
 elif sub_type == "ip-blocklist":
 config = {
 "ipExpression": policy.get("ipExpression", "#[attributes.remoteAddress]"),
 "ips": [ip.strip() for ip in policy.get("blockedIps", "").split(",") if ip.strip()]
 }
 elif sub_type == "basic-auth":
 config = {
 "username": policy.get("basicAuthUsername", ""),
 "password": policy.get("basicAuthPassword", "")
 }
 else:
 config = {}

 elif policy_type == "rate-limiting":
 sub_type = policy.get("rateLimitType", "rate-limit")
 template_id = POLICY_ASSET_MAP["rate-limiting"].get(sub_type, "rate-limiting")
 config = {
 "rateLimits": [
 {
 "maximumRequests": int(policy.get("maxRequests", 100)),
 "timePeriodInMilliseconds": int(policy.get("timePeriodMs", 60000))
 }
 ],
 "clusterizable": policy.get("clusterizable", "true") == "true",
 "exposeHeaders": policy.get("exposeHeaders", "false") == "true"
 }

 else:
 print(f"⚠️ Unknown policy type: {policy_type}")
 return None

 return {
 "policyTemplateId": template_id,
 "configurationData": config,
 "pointcutData": None,
 "order": int(policy.get("order", 1))
 }

def build_custom_policy_definition(policy):
 """
 Costruisce il payload per una custom policy
 pubblicata su Exchange. Non usa POLICY_ASSET_MAP
 in quanto il templateId coincide con il customPolicyAssetId.
 """
 try:
 config_data = json.loads(policy.get("customPolicyConfig", "{}"))
 except json.JSONDecodeError:
 print(f"❌ Invalid JSON in customPolicyConfig for {policy['assetId']}")
 sys.exit(1)

 return {
 "policyTemplateId": policy["customPolicyAssetId"],
 "groupId": policy.get("customPolicyGroupId", policy.get("groupId", "")),
 "assetId": policy["customPolicyAssetId"],
 "assetVersion": policy["customPolicyVersion"],
 "configurationData": config_data,
 "pointcutData": None,
 "order": int(policy.get("order", 10))
 }

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--policy-list", required=True)
 parser.add_argument("--api-instances", required=True)
 parser.add_argument("--cert-refs", required=True)
 parser.add_argument("--token", required=True)
 parser.add_argument("--org-id", required=True)
 parser.add_argument("--dry-run", default="false")
 args = parser.parse_args()

 with open(args.policy_list) as f:
 all_policies = json.load(f)
 with open(args.api_instances) as f:
 api_instances = json.load(f)
 with open(args.cert_refs) as f:
 cert_refs = json.load(f)
 with open(args.token) as f:
 token = json.load(f)["access_token"]

 dry_run = args.dry_run == "true"

 # Ordina per order — garantisce applicazione consistente
 all_policies_sorted = sorted(
 all_policies,
 key=lambda p: int(p.get("order", 99))
 )

 for policy in all_policies_sorted:
 asset_id = policy["assetId"]
 instance_info = api_instances.get(asset_id)
 if not instance_info:
 print(f"⚠️ No instance for {asset_id}, skipping.")
 continue

 env_id = instance_info["environmentId"]
 instance_id = instance_info["instanceId"]
 policy_type = policy["policyType"]

 print(f"\n🔧 Applying [{policy_type}] to: {asset_id} (order: {policy.get('order')})")

 # Build policy definition
 if policy_type == "custom":
 policy_def = build_custom_policy_definition(policy)
 else:
 policy_def = build_standard_policy_definition(policy, cert_refs)

 if not policy_def:
 continue

 # Verifica esistenza e applica/aggiorna
 existing = get_existing_policies(args.org_id, env_id, instance_id, token)
 existing_match = next(
 (p for p in existing
 if p.get("policyTemplateId") == policy_def.get("policyTemplateId")
 or p.get("assetId") == policy_def.get("assetId")),
 None
 )

 if existing_match:
 update_policy(
 args.org_id, env_id, instance_id,
 existing_match["id"], policy_def, token, dry_run
 )
 else:
 apply_policy(
 args.org_id, env_id, instance_id,
 policy_def, token, dry_run
 )

 print("\n✅ All policies applied.")