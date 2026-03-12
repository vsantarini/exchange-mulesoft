import json
import argparse
import os
from datetime import datetime, timezone

def build_report(deployments, policies, api_instances, env, dry_run):
 return {
 "reportGeneratedAt": datetime.now(timezone.utc).isoformat(),
 "environment": env,
 "dryRun": dry_run == "true",
 "executedBy": os.environ.get("BUILD_USER", "jenkins"),
 "buildNumber": os.environ.get("BUILD_NUMBER", "N/A"),
 "buildUrl": os.environ.get("BUILD_URL", "N/A"),
 "summary": {
 "totalApis": len(deployments),
 "totalPolicies": len(policies),
 "deployedInstances": len(api_instances)
 },
 "deployments": [
 {
 "assetId": d["assetId"],
 "version": d["assetVersion"],
 "gateway": d["gatewayName"],
 "environment": d["environmentId"],
 "endpointUri": d.get("endpointUri"),
 "proxyUri": d.get("proxyUri"),
 "instanceId": api_instances.get(d["assetId"], {}).get("instanceId"),
 "appliedPolicies": [
 {
 "type": p["policyType"],
 "order": p.get("order"),
 "templateId": p.get("policyTemplateId")
 }
 for p in policies if p["assetId"] == d["assetId"]
 ]
 }
 for d in deployments
 ]
 }

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--deployment-list", required=True)
 parser.add_argument("--policy-list", required=True)
 parser.add_argument("--api-instances", required=True)
 parser.add_argument("--env", required=True)
 parser.add_argument("--dry-run", default="false")
 parser.add_argument("--output", required=True)
 args = parser.parse_args()

 with open(args.deployment_list) as f:
 deployments = json.load(f)
 with open(args.policy_list) as f:
 policies = json.load(f)
 with open(args.api_instances) as f:
 api_instances = json.load(f)

 report = build_report(
 deployments, policies, api_instances,
 args.env, args.dry_run
 )

 with open(args.output, "w") as f:
 json.dump(report, f, indent=2)

 print(f"✅ Audit report generated.")
 print(f" ├── Environment : {args.env}")
 print(f" ├── APIs deployed : {report['summary']['totalApis']}")
 print(f" ├── Policies applied : {report['summary']['totalPolicies']}")
 print(f" └── Dry run : {args.dry_run}")