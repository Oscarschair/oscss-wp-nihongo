import json
import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

SCOPES = [
    'https://www.googleapis.com/auth/tagmanager.readonly',
    'https://www.googleapis.com/auth/tagmanager.edit.containers',
    'https://www.googleapis.com/auth/tagmanager.edit.containerversions',
    'https://www.googleapis.com/auth/tagmanager.publish'
]

CLIENT_SECRET_FILE = os.path.expanduser('~/.gemini/client_secret_20152954198-rbqiq5oc297qkg8hk9530srm5tvthgbr.apps.googleusercontent.com.json')
TOKEN_GTM_PATH = os.path.expanduser('~/.gemini/token_gtm.json')

print("Starting clean OAuth Flow for GTM Publish scope...", flush=True)
flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)

# Clean run_local_server (no double authorization_url)
print("Listening on port 8089. Opening browser...", flush=True)
creds = flow.run_local_server(port=8089, prompt='consent', access_type='offline', open_browser=True)

print("OAuth token acquired successfully!", flush=True)

token_data = {
    'token': creds.token,
    'refresh_token': creds.refresh_token,
    'token_uri': creds.token_uri,
    'client_id': creds.client_id,
    'client_secret': creds.client_secret,
    'scopes': creds.scopes,
    'universe_domain': creds.universe_domain if hasattr(creds, 'universe_domain') else 'googleapis.com',
    'account': ''
}
if creds.expiry:
    token_data['expiry'] = creds.expiry.isoformat()

with open(TOKEN_GTM_PATH, 'w', encoding='utf-8') as f:
    json.dump(token_data, f, indent=2)

print(f"Saved credentials to {TOKEN_GTM_PATH}", flush=True)

# Directly Publish Version 3 via GTM API
print("\nPublishing Version 3 (GA4 Google Tag: G-3QBPY87VPP) via Tag Manager API...", flush=True)
service = build('tagmanager', 'v2', credentials=creds)
version_path = "accounts/6004690865/containers/265349373/versions/3"

published_version = service.accounts().containers().versions().publish(path=version_path).execute()
print(f"SUCCESS: Version 3 Published! Response: {published_version}", flush=True)

# Verify live version
parent_container = "accounts/6004690865/containers/265349373"
live = service.accounts().containers().versions().live(parent=parent_container).execute()
print(f"\nVerified Current LIVE Version: ID {live.get('containerVersionId')} ({live.get('name')})", flush=True)
for t in live.get('tag', []):
    print(f"  Live Tag: [{t.get('type')}] {t.get('name')}", flush=True)
