import json
import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

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

print("Starting OAuth Flow for GTM Publish scope...", flush=True)
flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)

auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
print(f"\nAUTH_URL_START\n{auth_url}\nAUTH_URL_END\n", flush=True)

with open(os.path.expanduser('~/.gemini/gtm_auth_url_publish.txt'), 'w', encoding='utf-8') as f:
    f.write(auth_url)

print("Starting local server to receive auth code on port 8088...", flush=True)
creds = flow.run_local_server(port=8088, prompt='consent', access_type='offline', open_browser=True)

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

print("SUCCESS: Updated token_gtm.json with tagmanager.publish scope!", flush=True)
