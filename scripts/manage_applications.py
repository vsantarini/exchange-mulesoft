import json
import requests
import argparse

BASE_URL = "https://anypoint.mulesoft.com/exchange/api/v1/organizations"

def get_existing_apps(org_id, token):
    response = requests.get(
        f"{BASE_URL}/{org_id}/applications",
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    return {app["name"]: app for app in response.json()}

def create_application(app, org_id, token):
    response_create = requests.post(
        f"{BASE_URL}/{org_id}/applications",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "name": app["appName"],
            "description": app.get("description", ""),
            "url": app.get("url", ""),
            "redirectUri": [app["redirectUri"]] if app.get("redirectUri") else [],
            "grantTypes": [g.strip() for g in app.get("grantTypes", "client_credentials").split(",")],
            "apiEndpoints": False
        }
    )
    response_create.raise_for_status()
    result = response_create.json()
    print(f"[OK] Created app: {app['appName']} (id: {result['id']})")
    
    response_update = requests.post(
        f"{BASE_URL}/{org_id}/applications/{result['id']}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "name": app["appName"],
            "description": app.get("description", ""),
            "url": app.get("url", ""),
            "clientId": app.get("clientId", ""),
            "redirectUri": [app["redirectUri"]] if app.get("redirectUri") else [],
            "grantTypes": [g.strip() for g in app.get("grantTypes", "client_credentials").split(",")],
            "apiEndpoints": False
        }
    )
    response_update.raise_for_status()
    result_upd = response_update.json()
    print(f"[OK] Updated app: {app['appName']} (id: {result_upd['id']}), (client_id: {result_upd['clientId']})")
    
    return result

def update_application(app_id, app, org_id, token):
    response = requests.patch(
        f"{BASE_URL}/{org_id}/applications/{app_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "name": app["appName"],
            "description": app.get("description", ""),
            "url": app.get("url", ""),
            "clientId": app.get("clientId", "")
        }
    )
    response.raise_for_status()
    print(f"[OK] Updated app: {app['appName']} (id: {app_id})")
    return {"id": app_id, "name": app["appName"]}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--app-list", required=True)
    parser.add_argument("--token", required=True)
    parser.add_argument("--org-id", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.app_list) as f:
        apps = json.load(f)
    with open(args.token) as f:
        token = json.load(f)["access_token"]

    existing = get_existing_apps(args.org_id, token)
    app_ids = {}

    for app in apps:
        name = app["appName"]
        if name in existing:
            result = update_application(existing[name]["id"], app, args.org_id, token)
            app_ids[name] = existing[name]["id"]
        else:
            result = create_application(app, args.org_id, token)
            app_ids[name] = result["id"]
        # Store clientId/clientSecret if present
        if "clientId" in result:
            app_ids[f"{name}_clientId"] = result["clientId"]
            app_ids[f"{name}_clientSecret"] = result["clientSecret"]

    with open(args.output, "w") as f:
        json.dump(app_ids, f, indent=2)
    print("[OK] App IDs saved.")