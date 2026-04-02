import json
import requests
import argparse
import sys
import re
from datetime import datetime

BASE_URL = "https://anypoint.mulesoft.com/exchange/api/v1/organizations"

# ═══════════════════════════════════════════════════════════
# COSTRUZIONE MAPPA CERTIFICATI → SDN PER APP
# ═══════════════════════════════════════════════════════════

def build_cert_sdn_map(certs):
    """
    Costruisce un dizionario { appName: certSubjectDN }
    considerando solo i certificati con useAsClientId = True
    e senza errori di estrazione.
    """
    sdn_map = {}
    for cert in certs:
        if cert.get("_error"):
            print(f"[WARN] Certificato '{cert.get('certAlias')}' ignorato (errore di estrazione)")
            continue
        if cert.get("useAsClientId") is True:
            app_name = cert.get("appName", "")
            sdn = cert.get("certSubjectDN", "")
            if app_name and sdn:
                sdn_map[app_name] = sdn
                print(f"[INFO] App '{app_name}' → clientId da SDN: {sdn}")
            else:
                print(f"[WARN] Record certificato incompleto: appName='{app_name}', SDN='{sdn}'")
    return sdn_map


# ═══════════════════════════════════════════════════════════
# CALCOLO VERSIONE PROGRESSIVA
# ═══════════════════════════════════════════════════════════

def compute_next_version(base_name, existing_apps):
    """
    Cerca tra le app esistenti quelle il cui nome inizia con <base_name>_v
    e restituisce il prossimo progressivo disponibile.
    Esempio: se esistono my-app_v1_20260101, my-app_v2_20260315 → ritorna 3.
    """
    pattern = re.compile(rf"^{re.escape(base_name)}_v(\d+)_\d{{8}}$")
    max_version = 0

    for app_name in existing_apps:
        match = pattern.match(app_name)
        if match:
            version = int(match.group(1))
            max_version = max(max_version, version)

    return max_version + 1


def generate_versioned_name(base_name, version):
    """
    Genera il nome versionato: <base_name>_v<versione>_<YYYYMMDD>
    Esempio: my-consumer-app_v2_20260402
    """
    today = datetime.now().strftime("%Y%m%d")
    return f"{base_name}_v{version}_{today}"


# ═══════════════════════════════════════════════════════════
# OPERAZIONI CRUD APPLICAZIONI
# ═══════════════════════════════════════════════════════════

def get_existing_apps(org_id, token):
    response = requests.get(
        f"{BASE_URL}/{org_id}/applications",
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    return {app["name"]: app for app in response.json()}


def create_application(app_name, app, org_id, token, client_id):
    """Crea una nuova applicazione con il nome e il clientId specificati."""
    response_create = requests.post(
        f"{BASE_URL}/{org_id}/applications",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "name": app_name,
            "description": app.get("description", ""),
            "url": app.get("url", ""),
            "clientId": client_id,
            "clientSecret": "password",
            "redirectUri": [app["redirectUri"]] if app.get("redirectUri") else [],
            "grantTypes": [g.strip() for g in app.get("grantTypes", "client_credentials").split(",")],
            "apiEndpoints": False
        }
    )
    response_create.raise_for_status()
    result = response_create.json()
    print(f"[OK] Created app: {app_name} (id: {result['id']}, clientId: {client_id})")
    return result


def update_application(app_id, app_name, app, org_id, token):
    """Aggiorna i campi descrittivi di un'applicazione esistente (NO clientId)."""
    payload = {
        "name": app_name,
        "description": app.get("description", ""),
        "url": app.get("url", "")
    }
    response = requests.patch(
        f"{BASE_URL}/{org_id}/applications/{app_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=payload
    )
    response.raise_for_status()
    print(f"[OK] Updated app: {app_name} (id: {app_id}, clientId: invariato)")
    return {"id": app_id, "name": app_name}


# ═══════════════════════════════════════════════════════════
# LOGICA DI DECISIONE
# ═══════════════════════════════════════════════════════════

def resolve_application(app, org_id, token, existing_apps, client_id_override):
    """
    Determina l'azione corretta per ogni applicazione:
    - App non esiste → CREA (con SDN come clientId se previsto)
    - App esiste, clientId coincide o nessun override → AGGIORNA campi descrittivi
    - App esiste, clientId DIVERSO → CREA NUOVA con nome versionato
    """
    base_name = app["appName"]
    target_client_id = client_id_override or app.get("clientId", "")

    if base_name not in existing_apps:
        # ── Caso 1: applicazione non esiste → creazione diretta ──
        print(f"[INFO] App '{base_name}' non trovata. Creazione in corso...")
        result = create_application(base_name, app, org_id, token, target_client_id)
        return {
            "action": "CREATED",
            "name": base_name,
            "id": result["id"],
            "clientId": result.get("clientId", target_client_id)
        }

    existing_app = existing_apps[base_name]
    existing_client_id = existing_app.get("clientId", "")

    if not client_id_override or existing_client_id == target_client_id:
        # ── Caso 2: clientId coincide o nessun override → aggiornamento descrittivo ──
        print(f"[INFO] App '{base_name}' esistente, clientId invariato. Aggiornamento campi...")
        update_application(existing_app["id"], base_name, app, org_id, token)
        return {
            "action": "UPDATED",
            "name": base_name,
            "id": existing_app["id"],
            "clientId": existing_client_id
        }

    # ── Caso 3: clientId DIVERSO → nuova app con naming versionato ──
    print(f"[INFO] App '{base_name}' esistente con clientId diverso.")
    print(f"         Esistente : {existing_client_id}")
    print(f"         Richiesto : {target_client_id}")
    print(f"[INFO] Creazione nuova versione dell'applicazione...")

    next_version = compute_next_version(base_name, existing_apps)
    versioned_name = generate_versioned_name(base_name, next_version)

    result = create_application(versioned_name, app, org_id, token, target_client_id)
    return {
        "action": "CREATED_NEW_VERSION",
        "name": versioned_name,
        "originalName": base_name,
        "version": next_version,
        "id": result["id"],
        "clientId": result.get("clientId", target_client_id),
        "previousAppId": existing_app["id"],
        "previousClientId": existing_client_id
    }


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crea/Aggiorna Consumer Applications su Anypoint Exchange"
    )
    parser.add_argument("--app-list", required=True,
                        help="File JSON con la lista delle applicazioni")
    parser.add_argument("--token", required=True,
                        help="File JSON con l'access token")
    parser.add_argument("--org-id", required=True,
                        help="Organization ID di Anypoint")
    parser.add_argument("--cert-list", required=False, default=None,
                        help="File JSON arricchito con SDN dei certificati (cert-list-enriched.json)")
    parser.add_argument("--output", required=True,
                        help="File JSON di output con gli App ID creati/aggiornati")
    args = parser.parse_args()

    # ── Caricamento input ──
    with open(args.app_list) as f:
        apps = json.load(f)
    with open(args.token) as f:
        token = json.load(f)["access_token"]

    # ── Costruzione mappa SDN dai certificati ──
    sdn_map = {}
    if args.cert_list:
        try:
            with open(args.cert_list) as f:
                certs = json.load(f)
            sdn_map = build_cert_sdn_map(certs)
            print(f"[INFO] {len(sdn_map)} applicazione/i con clientId da certificato")
        except FileNotFoundError:
            print(f"[WARN] File certificati non trovato: {args.cert_list}. "
                  f"Proseguo senza override del clientId.")
    else:
        print("[INFO] Nessun file certificati fornito. clientId da Excel o default.")

    # ── Recupero applicazioni esistenti ──
    existing = get_existing_apps(args.org_id, token)
    results = []
    errors = 0

    # ── Processamento applicazioni ──
    for app in apps:
        name = app["appName"]
        client_id_override = sdn_map.get(name)

        try:
            result = resolve_application(app, args.org_id, token, existing, client_id_override)
            results.append(result)

            # Se è stata creata una nuova versione, aggiorna la mappa delle app esistenti
            # per gestire eventuali run successivi nella stessa esecuzione
            if result["action"] == "CREATED_NEW_VERSION":
                existing[result["name"]] = {
                    "id": result["id"],
                    "name": result["name"],
                    "clientId": result["clientId"]
                }

        except requests.exceptions.HTTPError as e:
            print(f"[ERROR] Errore per app '{name}': {e}")
            print(f"        Response: {e.response.text if e.response else 'N/A'}")
            results.append({"action": "ERROR", "name": name, "error": str(e)})
            errors += 1

    # ── Salvataggio output ──
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    # ── Report finale ──
    print(f"\n{'='*60}")
    created = sum(1 for r in results if r["action"] == "CREATED")
    updated = sum(1 for r in results if r["action"] == "UPDATED")
    versioned = sum(1 for r in results if r["action"] == "CREATED_NEW_VERSION")
    print(f"[REPORT] Totale: {len(apps)} applicazioni processate")
    print(f"         Create (nuove)  : {created}")
    print(f"         Aggiornate      : {updated}")
    print(f"         Nuove versioni  : {versioned}")
    print(f"         Errori          : {errors}")
    print(f"[OK] Output salvato in {args.output}")

    if errors > 0:
        sys.exit(1)