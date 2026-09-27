import json
import os
import sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

token_path = os.path.expanduser('~/.gemini/token_gtm.json')

with open(token_path, 'r', encoding='utf-8') as f:
    token_data = json.load(f)

creds = Credentials(
    token=token_data.get('token'),
    refresh_token=token_data.get('refresh_token'),
    token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
    client_id=token_data.get('client_id'),
    client_secret=token_data.get('client_secret'),
    scopes=token_data.get('scopes')
)

if creds.expired and creds.refresh_token:
    print("Token expired. Refreshing token...")
    creds.refresh(Request())
    # Save updated token
    token_data['token'] = creds.token
    if creds.expiry:
        token_data['expiry'] = creds.expiry.isoformat()
    with open(token_path, 'w', encoding='utf-8') as f:
        json.dump(token_data, f, indent=2)
    print("Token refreshed and saved.")

service = build('tagmanager', 'v2', credentials=creds)

print("=== Connecting to Google Tag Manager API v2 ===")
accounts = service.accounts().list().execute().get('account', [])
print(f"Found {len(accounts)} accounts:")

target_container = None
target_account = None

for acc in accounts:
    acc_id = acc.get('accountId')
    acc_name = acc.get('name')
    print(f"\nAccount: {acc_name} (ID: {acc_id})")
    
    # List containers
    containers = service.accounts().containers().list(parent=f"accounts/{acc_id}").execute().get('container', [])
    for c in containers:
        c_id = c.get('containerId')
        c_name = c.get('name')
        public_id = c.get('publicId')
        usage = c.get('usageContext', [])
        print(f"  - Container: {c_name} | Public ID: {public_id} (ID: {c_id}) | Context: {usage}")
        if public_id == 'GTM-K6NZHVDJ':
            target_container = c
            target_account = acc

if target_container:
    print(f"\nSUCCESS: Found Target Container: {target_container['publicId']} ({target_container['name']}) in Account {target_account['name']}!")
else:
    print("\nTarget Container GTM-K6NZHVDJ was not found in the listed accounts.")
