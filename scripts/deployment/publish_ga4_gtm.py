import json
import os
import sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

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
    creds.refresh(Request())
    token_data['token'] = creds.token
    if creds.expiry:
        token_data['expiry'] = creds.expiry.isoformat()
    with open(token_path, 'w', encoding='utf-8') as f:
        json.dump(token_data, f, indent=2)

service = build('tagmanager', 'v2', credentials=creds)

parent_ws = "accounts/6004690865/containers/265349373/workspaces/3"
parent_container = "accounts/6004690865/containers/265349373"

print("[1/3] Creating Container Version from Workspace 3...")
version_body = {
    'name': 'v3: GA4 Google Tag Publish (G-3QBPY87VPP)',
    'notes': 'Published GA4 Google Tag (G-3QBPY87VPP) with Initialization - All Pages trigger.'
}

created_version = service.accounts().containers().workspaces().create_version(
    path=parent_ws, body=version_body
).execute()

cv = created_version.get('containerVersion', {})
version_id = cv.get('containerVersionId')
print(f"Created Version ID: {version_id} ({cv.get('name')})")

print(f"\n[2/3] Publishing Version {version_id} to LIVE...")
version_path = f"{parent_container}/versions/{version_id}"
published = service.accounts().containers().versions().publish(path=version_path).execute()

print(f"SUCCESS: Version {version_id} is now LIVE!")

print("\n[3/3] Verifying tags in Live Version...")
live = service.accounts().containers().versions().live(parent=parent_container).execute()
print(f"Current LIVE Version ID: {live.get('containerVersionId')} ({live.get('name')})")
for t in live.get('tag', []):
    print(f"  - [{t.get('type')}] {t.get('name')}")
