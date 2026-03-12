import json
import requests
import argparse
import os

def update_home_page(api, token, org_id, docs_dir):
    doc_path = os.path.join(docs_dir, f"{api['assetId']}.md")
    if not os.path.exists(doc_path):
        print(f"⚠️ No doc found for {api['assetId']}, skipping.")
        return

    with open(doc_path, "r") as f:
        content = f.read()

    image_name = os.path.basename(api.get("imageFile", ""))
    if image_name:
        content += (
            f"\n\n---\n\n## Integration Pattern\n\n"
            f"![Integration Pattern](resources/{image_name})\n"
        )

    url = (
        f"https://anypoint.mulesoft.com/exchange/api/v2/assets"
        f"/{org_id}/{api['assetId']}/{api['version']}/pages/home"
    )
    response = requests.put(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type":  "application/json"
        },
        json={"content": content}
    )
    response.raise_for_status()
    print(f"✅ Home page updated for {api['assetId']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-list",  required=True)
    parser.add_argument("--token",     required=True)
    parser.add_argument("--org-id",    required=True)
    parser.add_argument("--docs-dir",  required=True)
    args = parser.parse_args()

    with open(args.api_list) as f:
        apis = json.load(f)
    with open(args.token) as f:
        token = json.load(f)["access_token"]

    for api in apis:
        update_home_page(api, token, args.org_id, args.docs_dir)