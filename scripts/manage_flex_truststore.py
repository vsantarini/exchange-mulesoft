import json
import requests
import argparse
import sys
import base64

SECRETS_BASE = "https://anypoint.mulesoft.com/secrets-manager/api/v1/organizations"

def get_secret_groups(org_id, env_id, token):
    """Recupera tutti i Secret Groups dell'ambiente."""
    response = requests.get(
        f"{SECRETS_BASE}/{org_id}/environments/{env_id}/secretGroups",
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    return response.json()

def find_secret_group(org_id, env_id, token, group_name):
    """Trova il Secret Group per nome."""
    groups = get_secret_groups(org_id, env_id, token)
    for group in groups.get("data", groups) if isinstance(groups, dict) else groups:
        if group.get("name") == group_name:
            return group
    return None

def get_truststores(org_id, env_id, token, secret_group_id):
    """Recupera i truststore nel Secret Group."""
    response = requests.get(
        f"{SECRETS_BASE}/{org_id}/environments/{env_id}/secretGroups/{secret_group_id}/truststores",
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    return response.json()

def create_truststore(org_id, env_id, token, secret_group_id, name, cert_pem):
    """Crea un nuovo truststore con il certificato."""
    response = requests.post(
        f"{SECRETS_BASE}/{org_id}/environments/{env_id}/secretGroups/{secret_group_id}/truststores",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "name": name,
            "type": "PEM",
            "trustStore": {
                "pemEncodedCertificates": cert_pem
            }
        }
    )
    response.raise_for_status()
    result = response.json()
    print(f"[OK] Truststore '{name}' creato (id: {result.get('id', 'N/A')})")
    return result

def add_cert_to_truststore(org_id, env_id, token, secret_group_id, truststore_id, cert_pem, cert_alias):
    """Aggiunge un certificato a un truststore esistente tramite PATCH."""
    response = requests.patch(
        f"{SECRETS_BASE}/{org_id}/environments/{env_id}/secretGroups/{secret_group_id}/truststores/{truststore_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "trustStore": {
                "pemEncodedCertificates": cert_pem
            }
        }
    )
    response.raise_for_status()
    print(f"[OK] Certificato '{cert_alias}' aggiunto al truststore (id: {truststore_id})")
    return response.json()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gestione Truststore Flex Gateway")
    parser.add_argument("--token", required=True, help="File JSON con access_token")
    parser.add_argument("--org-id", required=True, help="Organization ID")
    parser.add_argument("--env-id", required=True, help="Environment ID")
    parser.add_argument("--target-env", required=True, help="Nome ambiente target (dev, uat, prod)")
    parser.add_argument("--secret-group", required=True, help="Nome del Secret Group")
    parser.add_argument("--cert-file", required=True, help="Path al certificato PEM")
    parser.add_argument("--cert-sdn", required=True, help="File JSON con l'SDN del certificato")
    args = parser.parse_args()

    with open(args.token) as f:
        token = json.load(f)["access_token"]
    with open(args.cert_file) as f:
        cert_pem = f.read()
    with open(args.cert_sdn) as f:
        cert_sdn = json.load(f)["sdn"]

    # ── 1. Verifica che il Secret Group esista ──
    print(f"[INFO] Ricerca Secret Group '{args.secret_group}' nell'ambiente '{args.target_env}'...")
    secret_group = find_secret_group(args.org_id, args.env_id, token, args.secret_group)

    if not secret_group:
        print(f"[ERROR] Secret Group '{args.secret_group}' NON trovato nell'ambiente '{args.target_env}' (env-id: {args.env_id}).")
        print("[ERROR] Assicurarsi che il Secret Group sia stato creato prima di eseguire questa pipeline.")
        sys.exit(1)

    secret_group_id = secret_group["id"]
    print(f"[OK] Secret Group trovato (id: {secret_group_id})")

    # ── 2. Verifica che il truststore esista nel Secret Group ──
    truststore_name = f"truststore-flex-{args.target_env}"
    truststores = get_truststores(args.org_id, args.env_id, token, secret_group_id)

    existing_ts = None
    ts_list = truststores.get("data", truststores) if isinstance(truststores, dict) else truststores
    for ts in ts_list:
        if ts.get("name") == truststore_name:
            existing_ts = ts
            break

    # ── 3. Crea o aggiorna il truststore ──
    cert_alias = cert_sdn.replace(",", "_").replace("=", "-").replace(" ", "")

    if existing_ts:
        print(f"[INFO] Truststore '{truststore_name}' già esistente, aggiunta certificato...")
        add_cert_to_truststore(
            args.org_id, args.env_id, token,
            secret_group_id, existing_ts["id"],
            cert_pem, cert_alias
        )
    else:
        print(f"[INFO] Truststore '{truststore_name}' non trovato, creazione in corso...")
        create_truststore(
            args.org_id, args.env_id, token,
            secret_group_id, truststore_name, cert_pem
        )

    print(f"[OK] Operazione completata per ambiente '{args.target_env}'.")