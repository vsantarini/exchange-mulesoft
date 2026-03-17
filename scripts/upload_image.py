import json
import requests
import argparse
import os

def upload_image(api, token, org_id):
    image_path = api.get("imageFile")
    if not image_path or not os.path.exists(image_path):
        print(f"⚠️ No image found for {api['assetId']}, skipping.")
        return None

    url = (
        f"https://anypoint.mulesoft.com/exchange/api/v2/assets"
        f"/{org_id}/{api['assetId']}/{api['version']}/portal/draft/resources"
    )
    image_name = os.path.basename(image_path)

    with open(image_path, "rb") as f:
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            files={"file": (image_name, f)},
            data={"name": image_name}
        )
    response.raise_for_status()
    print(f"✅ Image uploaded for {api['assetId']}: {image_name}")
    return image_name

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
        upload_image(api, token, args.org_id)