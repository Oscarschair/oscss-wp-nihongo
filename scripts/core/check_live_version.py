import json
import os
import sys
from google.oauth2.credentials import Credentials
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

service = build('tagmanager', 'v2', credentials=creds)

parent = "accounts/6004690865/containers/265349373"

# List version headers
versions = service.accounts().containers().version_headers().list(parent=parent).execute().get('containerVersionHeader', [])
print(f"Container Versions ({len(versions)}):")
for v in versions:
    print(f"  - Version ID: {v.get('containerVersionId')} | Name: {v.get('name')} | Deleted: {v.get('deleted')}")

# Check live version
try:
    live = service.accounts().containers().versions().live(parent=parent).execute()
    print(f"\nCurrent LIVE Version: ID {live.get('containerVersionId')} ({live.get('name')})")
    tags = live.get('tag', [])
    print(f"Tags in Live Version ({len(tags)}):")
    for t in tags:
        print(f"  - [{t.get('type')}] {t.get('name')}")
except Exception as e:
    print(f"No live version yet or error: {e}")
