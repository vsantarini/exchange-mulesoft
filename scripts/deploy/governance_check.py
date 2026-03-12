import json
import argparse
import sys

# Regole di governance per ambiente
GOVERNANCE_RULES = {
 "prod": {
 "required_policy_types": ["mtls", "security", "rate-limiting", "request-validation"],
 "routing_required": True,
 "mtls_mandatory": True,
 "min_rate_limit": 10
 },
 "test": {
 "required_policy_types": ["security", "rate-limiting"],
 "routing_required": True,
 "mtls_mandatory": False,
 "min_rate_limit": 1
 },
 "dev": {
 "required_policy_types": ["routing"],
 "routing_required": True,
 "mtls_mandatory": False,
 "min_rate_limit": 1
 }
}

def check_governance(deployments, policies, env, dry_run):
 rules = GOVERNANCE_RULES.get(env, {})
 errors = []
 warnings = []

 for d in deployments:
 asset_id = d["assetId"]
 asset_policies = [p for p in policies if p["assetId"] == asset_id]
 policy_types = [p["policyType"] for p in asset_policies]

 # Check required policy types
 for required in rules.get("required_policy_types", []):
 if required not in policy_types:
 errors.append(
 f"[{asset_id}] Missing required policy '{required}' for env '{env}'"
 )

 # Check mTLS mandatory
 if rules.get("mtls_mandatory") and "mtls" not in policy_types:
 errors.append(f"[{asset_id}] mTLS is mandatory in '{env}'")

 # Check routing
 if rules.get("routing_required") and "routing" not in policy_types:
 errors.append(f"[{asset_id}] Routing policy is required in '{env}'")

 # Check rate limit values
 for p in asset_policies:
 if p["policyType"] == "rate-limiting":
 max_req = int(p.get("maxRequests", 0))
 if max_req < rules.get("min_rate_limit", 1):
 warnings.append(
 f"[{asset_id}] Rate limit ({max_req}) below minimum "
 f"({rules['min_rate_limit']}) for env '{env}'"
 )

 # Check policy order consistency
 orders = [int(p.get("order", 0)) for p in asset_policies]
 if len(orders) != len(set(orders)):
 errors.append(f"[{asset_id}] Duplicate policy order values detected")

 return errors, warnings

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--deployment-list", required=True)
 parser.add_argument("--policy-list", required=True)
 parser.add_argument("--env", required=True)
 parser.add_argument("--dry-run", default="false")
 args = parser.parse_args()

 with open(args.deployment_list) as f:
 deployments = json.load(f)
 with open(args.policy_list) as f:
 policies = json.load(f)

 errors, warnings = check_governance(
 deployments, policies,
 args.env, args.dry_run == "true"
 )

 for w in warnings:
 print(f"⚠️ WARNING: {w}")
 for e in errors:
 print(f"❌ ERROR: {e}")

 if errors:
 if args.dry_run == "true":
 print("⚠️ DRY RUN — governance errors found but not blocking.")
 else:
 sys.exit(1)
 else:
 print("✅ Governance check passed.")