import json
import requests
import argparse

BASE_URL = "https://anypoint.mulesoft.com/exchange/api/v2/organizations"

def get_existing_categories(org_id, token):
 response = requests.get(
 f"{BASE_URL}/{org_id}/categories",
 headers={"Authorization": f"Bearer {token}"}
 )
 response.raise_for_status()
 return {cat["displayName"]: cat for cat in response.json()}

def create_category(category, org_id, token):
 category_name = category.split(':')[0].strip()
 category_value = category.split(':')[1].strip()
 response = requests.post(
 f"{BASE_URL}/{org_id}/categories",
 headers={
 "Authorization": f"Bearer {token}",
 "Content-Type": "application/json"
 },
 json={
 "displayName": category_name,
 "acceptedValues": [category_value],
 "tagKey": category_name,
 "assetTypeRestrictions": ["rest-api", "soap-api"],
 }
 )
 response.raise_for_status()
 print(f"✅ Category created: {category_name}")

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--api-list", required=True)
 parser.add_argument("--token", required=True)
 parser.add_argument("--org-id", required=True)
 args = parser.parse_args()

 with open(args.api_list) as f:
    apis = json.load(f)
 with open(args.token) as f:
    token = json.load(f)["access_token"]

 existing = get_existing_categories(args.org_id, token)

 # Collect all unique categories from Excel
 required = set()
 for api in apis:
    for cat in str(api.get("categories", "")).split(","):
        cat = cat.strip()
        if cat:
            required.add(cat)

 for cat in required:
    if cat.split(':')[0].strip() not in existing:
        print(f"|WARN| Category '{cat}' not found — creating it...")
        create_category(cat, args.org_id, token)
    else:
        print(f"|OK| Category '{cat.split(':')[0].strip()}' already exists.")