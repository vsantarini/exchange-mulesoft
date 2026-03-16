import json
import requests
import argparse
import os
import xml.dom.minidom

BASE_URL = "https://anypoint.mulesoft.com/exchange/api/v2/assets"

def prettify_xml(file_path):
    """Formatta l'XML per una migliore leggibilita'."""
    with open(file_path, "r", encoding="utf-8") as f:
        raw = f.read()
    try:
        dom = xml.dom.minidom.parseString(raw)
        return dom.toprettyxml(indent="  ")
    except Exception:
        return raw

def get_file_type(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".wsdl":
        return "WSDL"
    elif ext == ".xsd":
        return "XSD"
    return "FILE"

def build_page_content(file_path):
    """Genera il contenuto Markdown della pagina per un WSDL o XSD."""
    file_name = os.path.basename(file_path)
    file_type = get_file_type(file_path)
    xml_content = prettify_xml(file_path)

    return (
        f"# {file_type}: `{file_name}`\n\n"
        f"> This page contains the full content of the **{file_type}** "
        f"file `{file_name}` included in this service definition.\n\n"
        f"---\n\n"
        f"## File Content\n\n"
        f"```xml\n"
        f"{xml_content}\n"
        f"```\n"
    )

def get_page_name(file_path):
    """Genera un nome pagina URL-safe dal nome del file."""
    base = os.path.splitext(os.path.basename(file_path))[0]
    file_type = get_file_type(file_path).lower()
    return f"{file_type}-{base}".lower().replace("_", "-").replace(" ", "-")

def create_or_update_page(api, page_name, content, token, org_id):
    url = f"{BASE_URL}/{org_id}/{api['assetId']}/{api['version']}/pages/{page_name}"
    response = requests.put(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={"content": content}
    )
    response.raise_for_status()
    print(f" [OK] Page created/updated: {page_name}")

def publish_page(api, page_name, token, org_id):
    url = f"{BASE_URL}/{org_id}/{api['assetId']}/{api['version']}/pages/{page_name}/publish"
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    print(f" [OK] Page published: {page_name}")

def build_index_content(api, files_info):
    """Genera una pagina indice con la lista di tutti i WSDL/XSD."""
    lines = [
        f"# Service Definition Index\n\n",
        f"> This page provides an overview of all **WSDL** and **XSD** files "
        f"included in the `{api['name']}` service.\n\n",
        f"---\n\n",
        f"## Files\n\n",
        f"| File | Type | Description |\n",
        f"|---|---|---|\n"
    ]
    for info in files_info:
        page_name = info["pageName"]
        file_name = info["fileName"]
        file_type = info["fileType"]
        desc = "Entry-point" if info["isMain"] else "Dependency"
        lines.append(f"| [{file_name}]({page_name}) | `{file_type}` | {desc} |\n")

    return "".join(lines)

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
        if api["type"] != "soap":
            continue

        print(f"\n[INFO] Processing SOAP pages for: {api['assetId']}")

        # Raccoglie tutti i file WSDL e XSD
        all_files = [api["filePath"]]
        if api.get("additionalFiles"):
            extras = [f.strip() for f in api["additionalFiles"].split("|") if f.strip()]
            all_files.extend(extras)

        files_info = []
        for file_path in all_files:
            if not os.path.exists(file_path):
                print(f"[WARN] File not found, skipping: {file_path}")
                continue

            page_name = get_page_name(file_path)
            content = build_page_content(file_path)
            file_type = get_file_type(file_path)

            create_or_update_page(api, page_name, content, token, args.org_id)
            publish_page(api, page_name, token, args.org_id)

            files_info.append({
                "pageName": page_name,
                "fileName": os.path.basename(file_path),
                "fileType": file_type,
                "isMain": file_path == api["filePath"]
            })

        # Crea pagina indice
        if files_info:
            index_content = build_index_content(api, files_info)
            create_or_update_page(api, "service-definition", index_content, token, args.org_id)
            publish_page(api, "service-definition", token, args.org_id)
            print(f"[OK] Index page created for: {api['assetId']}")