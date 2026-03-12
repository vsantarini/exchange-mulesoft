import json
import requests
import argparse

def assign_tags_and_categories(api, token, org_id):
    base = (
        f"https://anypoint.mulesoft.com/exchange/api/v2/assets"
        f"/{org_id}/{api['assetId']}/{api['version']}"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json"
    }

    # Assign Tags
    tags = [{"value": t.strip()} for t in api.get("tags", "").split(",") if t.strip()]
    if tags:
        requests.put(f"{base}/tags", headers=headers, json=tags).raise_for_status()
        print(f"✅ Tags assigned to {api['assetId']}: {tags}")

    # Assign Categories
    categories = [c.strip() for c in api.get("categories", "").split(",") if c.strip()]
    for category in categories:
        requests.put(
            f"{base}/tags/fields/category/tags/{category}",
            headers=headers
        ).raise_for_status()
    print(f"✅ Categories assigned to {api['assetId']}: {categories}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-list", required=True)
    parser.add_argument("--token",    required=True)
    parser.add_argument("--org-id",   required=True)
    args = parser.parse_args()

    with open(args.api_list) as f:
        apis = json.load(f)
    with open(args.token) as f:
        token = json.load(f)["access_token"]

    for api in apis:
        assign_tags_and_categories(api, token, args.org_id)