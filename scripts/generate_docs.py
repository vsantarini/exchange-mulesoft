import json
import os
import argparse
import yaml
from openai import OpenAI

def read_spec(file_path):
    with open(file_path, "r") as f:
        if file_path.endswith(".wsdl") or file_path.endswith(".xml"):
            return f.read()
        return yaml.dump(yaml.safe_load(f))

def generate_documentation(spec_content, api_name, client):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a technical writer. Given an API specification "
                    "(Swagger/OAS or WSDL), generate a clear and detailed "
                    "documentation page in Markdown format explaining: "
                    "purpose, endpoints/operations, request/response examples, "
                    "and integration notes."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Generate documentation for the API '{api_name}'.\n\n"
                    f"Specification:\n{spec_content}"
                )
            }
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-list",   required=True)
    parser.add_argument("--openai-key", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    client = OpenAI(api_key=args.openai_key)

    with open(args.api_list) as f:
        apis = json.load(f)

    for api in apis:
        print(f"📝 Generating docs for: {api['assetId']}")
        spec = read_spec(api["filePath"])
        doc  = generate_documentation(spec, api["name"], client)
        out  = os.path.join(args.output_dir, f"{api['assetId']}.md")
        with open(out, "w") as f:
            f.write(doc)
        print(f"✅ Documentation saved: {out}")