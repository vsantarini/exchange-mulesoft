import json
import requests
import argparse

def publish_page(api, token, org_id):
    url = (
        f"https://anypoint.mulesoft.com/exchange/api/v2/assets"
        f"/{org_id}/{api['assetId']}/{api['version']}/pages/home/publish"
    )
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    print(f"✅ Page published for {api['assetId']}")

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
        publish_page(api, token, args.org_id)