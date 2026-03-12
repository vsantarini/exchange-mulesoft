import requests
import json
import argparse
import time
import threading

TOKEN_FILE = "token.json"
REFRESH_MARGIN = 300 # refresh 5 min before expiry

def fetch_token(client_id, client_secret):
 r = requests.post(
 "https://anypoint.mulesoft.com/accounts/api/v2/oauth2/token",
 headers={"Content-Type": "application/x-www-form-urlencoded"},
 data={
 "grant_type": "client_credentials",
 "client_id": client_id,
 "client_secret": client_secret
 }
 )
 r.raise_for_status()
 data = r.json()
 data["fetched_at"] = time.time()
 return data

def save_token(data, output):
 with open(output, "w") as f:
 json.dump(data, f)

def start_refresh_daemon(client_id, client_secret, output, expires_in):
 def refresh():
 sleep_time = max(expires_in - REFRESH_MARGIN, 60)
 time.sleep(sleep_time)
 print("🔄 Refreshing token...")
 data = fetch_token(client_id, client_secret)
 save_token(data, output)
 print("✅ Token refreshed.")

 t = threading.Thread(target=refresh, daemon=True)
 t.start()

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--client-id", required=True)
 parser.add_argument("--client-secret", required=True)
 parser.add_argument("--output", required=True)
 args = parser.parse_args()

 data = fetch_token(args.client_id, args.client_secret)
 save_token(data, args.output)
 print(f"✅ Token acquired. Expires in: {data.get('expires_in', 'N/A')}s")