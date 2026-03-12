import json
import requests
import argparse
import os
import zipfile
import tempfile

def create_soap_bundle(api):
 """
 Crea uno ZIP contenente tutti i WSDL e XSD del servizio SOAP.
 La struttura attesa nell'Excel è:
 - filePath: WSDL entry-point
 - additionalFiles: lista di path separati da | (altri WSDL e XSD)
 """
 tmp = tempfile.mkdtemp()
 zip_path = os.path.join(tmp, f"{api['assetId']}.zip")

 # Raccoglie tutti i file
 all_files = [api["filePath"]]
 if api.get("additionalFiles"):
 extras = [f.strip() for f in api["additionalFiles"].split("|") if f.strip()]
 all_files.extend(extras)

 with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
 for file_path in all_files:
 if not os.path.exists(file_path):
 print(f"⚠️ File not found, skipping: {file_path}")
 continue
 # Mantiene la struttura relativa delle directory
 arcname = os.path.relpath(file_path, start=os.path.dirname(api["filePath"]))
 zf.write(file_path, arcname)
 print(f" ├── Added to bundle: {arcname}")

 return zip_path

def publish_asset(api, token, org_id):
 is_soap = api["type"] == "soap"
 classifier = "wsdl" if is_soap else "oas"
 main_file = os.path.basename(api["filePath"])
 url = "https://anypoint.mulesoft.com/exchange/api/v2/assets"

 headers = {"Authorization": f"Bearer {token}"}

 if is_soap:
 # Crea bundle ZIP per SOAP multi-file
 print(f"📦 Creating SOAP bundle for: {api['assetId']}")
 zip_path = create_soap_bundle(api)
 with open(zip_path, "rb") as f:
 response = requests.post(
 url,
 headers=headers,
 data={
 "organizationId": org_id,
 "groupId": org_id,
 "assetId": api["assetId"],
 "version": api["version"],
 "name": api["name"],
 "classifier": classifier,
 "apiVersion": api["apiVersion"],
 "main": main_file
 },
 files={"file": (f"{api['assetId']}.zip", f, "application/zip")}
 )
 else:
 # REST — upload singolo file
 with open(api["filePath"], "rb") as f:
 response = requests.post(
 url,
 headers=headers,
 data={
 "organizationId": org_id,
 "groupId": org_id,
 "assetId": api["assetId"],
 "version": api["version"],
 "name": api["name"],
 "classifier": classifier,
 "apiVersion": api["apiVersion"],
 "main": main_file
 },
 files={"file": (main_file, f)}
 )

 response.raise_for_status()
 print(f"✅ Published: {api['assetId']} v{api['version']}")

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

 for api in apis:
 publish_asset(api, token, args.org_id)