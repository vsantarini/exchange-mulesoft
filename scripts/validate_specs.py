import json
import argparse
import subprocess
import os
import sys

SPECTRAL_BINARY = "spectral"

def check_spectral_installed():
 result = subprocess.run(
 ["which", SPECTRAL_BINARY],
 capture_output=True
 )
 if result.returncode != 0:
 print("❌ Spectral CLI not found. Install it with: npm install -g @stoplight/spectral-cli")
 sys.exit(1)

def get_ruleset(api):
 """
 Ruleset resolution priority:
 1. Per-API custom ruleset defined in Excel (customRuleset column)
 2. Default ruleset per type (rest/soap)
 3. Fallback to built-in Spectral ruleset
 """
 if api.get("customRuleset") and os.path.exists(api["customRuleset"]):
 return api["customRuleset"]
 default_map = {
 "rest": "rulesets/default-oas.yaml",
 "soap": "rulesets/default-wsdl.yaml"
 }
 default = default_map.get(api["type"])
 if default and os.path.exists(default):
 return default
 return None # fallback to Spectral built-in

def validate_with_spectral(api):
 ruleset = get_ruleset(api)
 cmd = [SPECTRAL_BINARY, "lint", api["filePath"], "--format", "json"]
 if ruleset:
 cmd += ["--ruleset", ruleset]

 print(f"🔍 Validating: {api['assetId']} | Ruleset: {ruleset or 'built-in'}")
 result = subprocess.run(cmd, capture_output=True, text=True)

 # Save Spectral output for archiving
 output_path = f"spectral-reports/{api['assetId']}.json"
 os.makedirs("spectral-reports", exist_ok=True)
 with open(output_path, "w") as f:
 f.write(result.stdout)

 # Parse results
 try:
 issues = json.loads(result.stdout) if result.stdout.strip() else []
 except json.JSONDecodeError:
 issues = []

 errors = [i for i in issues if i.get("severity") == 0] # 0 = error
 warnings = [i for i in issues if i.get("severity") == 1] # 1 = warning
 hints = [i for i in issues if i.get("severity") == 2] # 2 = hint

 print(f" ├── ❌ Errors: {len(errors)}")
 print(f" ├── ⚠️ Warnings: {len(warnings)}")
 print(f" └── 💡 Hints: {len(hints)}")

 if errors:
 print(f"\n❌ Validation failed for {api['assetId']}:")
 for e in errors:
 path = " > ".join(str(p) for p in e.get("path", []))
 print(f" - [{e.get('code')}] {e.get('message')} @ {path} (line {e.get('range', {}).get('start', {}).get('line', '?')})")
 return False

 return True

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--api-list", required=True)
 parser.add_argument("--fail-on-warnings", action="store_true", default=False)
 args = parser.parse_args()

 check_spectral_installed()

 with open(args.api_list) as f:
 apis = json.load(f)

 failed = []
 for api in apis:
 ok = validate_with_spectral(api)
 if not ok:
 failed.append(api["assetId"])

 if failed:
 print(f"\n❌ Validation failed for: {', '.join(failed)}")
 sys.exit(1)
 else:
 print("\n✅ All specs validated successfully.")