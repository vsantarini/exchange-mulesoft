import json
import argparse
import os
from jinja2 import Template

AUTODISCOVERY_TEMPLATE = """
# Auto-generated Autodiscovery Configuration
# Asset: {{ asset_id }} | Environment: {{ env_id }}

anypoint:
 autodiscovery:
 serviceUrl: https://anypoint.mulesoft.com
 apiId: "{{ instance_id }}"
 flowName: "{{ flow_name }}"
 apikitRef: "{{ apikit_ref }}"
"""

PROPERTIES_TEMPLATE = """
# Auto-generated properties file
# Asset: {{ asset_id }}

anypoint.platform.client_id={{ client_id_placeholder }}
anypoint.platform.client_secret={{ client_secret_placeholder }}
api.id={{ instance_id }}
"""

def generate_autodiscovery(deployment, instance_info, output_dir, dry_run):
 asset_id = deployment["assetId"]
 instance_id = instance_info["instanceId"]
 env_id = instance_info["environmentId"]

 if dry_run:
 print(f"[DRY RUN] Would generate autodiscovery config for: {asset_id}")
 return

 os.makedirs(output_dir, exist_ok=True)

 # Genera global.yaml
 yaml_content = Template(AUTODISCOVERY_TEMPLATE).render(
 asset_id=asset_id,
 instance_id=instance_id,
 env_id=env_id,
 flow_name=deployment.get("flowName", f"{asset_id}-main"),
 apikit_ref=deployment.get("apikitRef", f"{asset_id}-config")
 )
 yaml_path = os.path.join(output_dir, f"{asset_id}-autodiscovery.yaml")
 with open(yaml_path, "w") as f:
 f.write(yaml_content)

 # Genera properties file
 props_content = Template(PROPERTIES_TEMPLATE).render(
 asset_id=asset_id,
 instance_id=instance_id,
 client_id_placeholder="${anypoint.client_id}",
 client_secret_placeholder="${anypoint.client_secret}"
 )
 props_path = os.path.join(output_dir, f"{asset_id}.properties")
 with open(props_path, "w") as f:
 f.write(props_content)

 print(f"✅ Autodiscovery config generated: {yaml_path}")
 print(f"✅ Properties file generated: {props_path}")

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--api-instances", required=True)
 parser.add_argument("--deployment-list", required=True)
 parser.add_argument("--dry-run", default="false")
 parser.add_argument("--output", required=True)
 args = parser.parse_args()

 with open(args.deployment_list) as f:
 deployments = json.load(f)
 with open(args.api_instances) as f:
 api_instances = json.load(f)

 dry_run = args.dry_run == "true"

 for d in deployments:
 asset_id = d["assetId"]
 instance_info = api_instances.get(asset_id)
 if not instance_info:
 print(f"⚠️ No instance for {asset_id}, skipping autodiscovery.")
 continue
 generate_autodiscovery(d, instance_info, args.output, dry_run)