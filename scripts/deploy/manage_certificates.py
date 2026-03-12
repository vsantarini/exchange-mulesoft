import json
import requests
import argparse
import os
import hvac
import base64

ANYPOINT_SECRET_URL = "https://anypoint.mulesoft.com/secrets-manager/api/v1/organizations"

def get_cert_from_vault(vault_client, secret_path):
 """Recupera certificato da HashiCorp Vault."""
 secret = vault_client.secrets.kv.read_secret_version(path=secret_path)
 return secret["data"]["data"]

def upload_to_secret_manager(org_id, env_id, name, cert_data, token, dry_run):
 """Carica il certificato su Anypoint Secret Manager."""
 if dry_run:
 print(f"[DRY RUN] Would upload cert: {name}")
 return f"dry-run-secret-{name}"

 url = f"{ANYPOINT_SECRET_URL}/{org_id}/environments/{env_id}/secretGroups"

 # Step 1: Crea/verifica secret group
 r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
 r.raise_for_status()
 groups = r.json()
 group_id = next((g["id"] for g in groups if g["name"] == "cicd-certs"), None)

 if not group_id:
 r = requests.post(
 url,
 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
 json={"name": "cicd-certs"}
 )
 r.raise_for_status()
 group_id = r.json()["id"]

 # Step 2: Upload TLS Context
 tls_url = f"{url}/{group_id}/tlsContexts"
 payload = {
 "name": name,
 "tlsEnabledProtocols": ["TLSv1.2", "TLSv1.3"],
 "keystore": {
 "type": "PEM",
 "certificateFile": base64.b64encode(
 cert_data.get("certificate", "").encode()
 ).decode(),
 "keyFile": base64.b64encode(
 cert_data.get("privateKey", "").encode()
 ).decode()
 },
 "truststore": {
 "type": "PEM",
 "certificateFile": base64.b64encode(
 cert_data.get("caCertificate", "").encode()
 ).decode()
 }
 }

 r = requests.post(
 tls_url,
 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
 json=payload
 )
 r.raise_for_status()
 secret_id = r.json()["id"]
 print(f"✅ Certificate uploaded: {name} (id: {secret_id})")
 return secret_id

def check_cert_expiry(cert_data):
 """Verifica scadenza certificato."""
 from cryptography import x509
 from cryptography.hazmat.backends import default_backend
 from datetime import datetime, timezone

 cert_pem = cert_data.get("certificate", "")
 if not cert_pem:
 return None

 cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())
 expiry = cert.not_valid_after_utc
 days_left = (expiry - datetime.now(timezone.utc)).days

 if days_left < 30:
 print(f"⚠️ Certificate expires in {days_left} days!")
 else:
 print(f"✅ Certificate valid for {days_left} days.")

 return days_left

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--policy-list", required=True)
 parser.add_argument("--token", required=True)
 parser.add_argument("--org-id", required=True)
 parser.add_argument("--vault-token", required=True)
 parser.add_argument("--vault-addr", required=True)
 parser.add_argument("--dry-run", default="false")
 parser.add_argument("--output", required=True)
 args = parser.parse_args()

 with open(args.policy_list) as f:
 policies = json.load(f)
 with open(args.token) as f:
 token = json.load(f)["access_token"]

 vault_client = hvac.Client(
 url=args.vault_addr,
 token=args.vault_token
 )

 cert_refs = {}
 dry_run = args.dry_run == "true"

 for policy in policies:
 if policy.get("policyType") != "mtls":
 continue

 vault_path = policy.get("vaultCertPath")
 asset_id = policy["assetId"]

 if not vault_path:
 print(f"⚠️ No vaultCertPath for {asset_id}, skipping.")
 continue

 print(f"🔐 Processing certificates for: {asset_id}")
 cert_data = get_cert_from_vault(vault_client, vault_path)
 check_cert_expiry(cert_data)

 secret_id = upload_to_secret_manager(
 args.org_id,
 policy["environmentId"],
 f"cert-{asset_id}",
 cert_data,
 token,
 dry_run
 )
 cert_refs[asset_id] = secret_id

 with open(args.output, "w") as f:
 json.dump(cert_refs, f, indent=2)
 print("✅ Certificate references saved.")