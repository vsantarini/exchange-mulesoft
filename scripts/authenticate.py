import requests
import json
import argparse
import sys
import time

ANYPOINT_TOKEN_URL = "https://anypoint.mulesoft.com/accounts/api/v2/oauth2/token"

def fetch_token(client_id, client_secret):
 """
 Fetches an OAuth2 access token using client credentials flow.
 """
 try:
 r = requests.post(
 ANYPOINT_TOKEN_URL,
 headers={"Content-Type": "application/x-www-form-urlencoded"},
 data={
 "grant_type": "client_credentials",
 "client_id": client_id,
 "client_secret": client_secret
 },
 timeout=30
 )
 r.raise_for_status()
 data = r.json()
 data["fetched_at"] = time.time()
 return data

 except requests.exceptions.HTTPError as e:
 print(f"❌ HTTP error during authentication: {e}")
 print(f" Response: {e.response.text}")
 sys.exit(1)

 except requests.exceptions.ConnectionError:
 print("❌ Connection error — check network access to anypoint.mulesoft.com")
 sys.exit(1)

 except requests.exceptions.Timeout:
 print("❌ Request timed out during authentication.")
 sys.exit(1)

 except Exception as e:
 print(f"❌ Unexpected error: {e}")
 sys.exit(1)

def validate_token(data):
 """
 Validates the token response contains required fields.
 """
 required = ["access_token", "token_type", "expires_in"]
 for field in required:
 if field not in data:
 print(f"❌ Token response missing field: {field}")
 sys.exit(1)

if __name__ == "__main__":
 parser = argparse.ArgumentParser(
 description="Authenticate to Anypoint Platform via OAuth2 client credentials."
 )
 parser.add_argument("--client-id", required=True, help="Anypoint Connected App client ID")
 parser.add_argument("--client-secret", required=True, help="Anypoint Connected App client secret")
 parser.add_argument("--output", required=True, help="Output file path for token JSON")
 args = parser.parse_args()

 print("🔐 Authenticating to Anypoint Platform...")
 token_data = fetch_token(args.client_id, args.client_secret)
 validate_token(token_data)

 with open(args.output, "w") as f:
 json.dump(token_data, f, indent=2)

 print(f"✅ Authentication successful.")
 print(f" ├── Token type : {token_data['token_type']}")
 print(f" ├── Expires in : {token_data['expires_in']}s")
 print(f" └── Saved to : {args.output}")