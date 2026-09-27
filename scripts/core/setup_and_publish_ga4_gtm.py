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
    creds.refresh(Request())
    token_data['token'] = creds.token
    if creds.expiry:
        token_data['expiry'] = creds.expiry.isoformat()
    with open(token_path, 'w', encoding='utf-8') as f:
        json.dump(token_data, f, indent=2)

service = build('tagmanager', 'v2', credentials=creds)

parent = "accounts/6004690865/containers/265349373/workspaces/2"

# 1. Check existing triggers
triggers = service.accounts().containers().workspaces().triggers().list(parent=parent).execute().get('trigger', [])
print(f"Existing Triggers: {len(triggers)}")
all_pages_trigger_id = None
for tr in triggers:
    print(f"  Trigger: {tr['name']} (ID: {tr['triggerId']}, Type: {tr['type']})")
    if tr['type'] in ['pageview', 'always', 'init']:
        all_pages_trigger_id = tr['triggerId']

# 2. If no trigger exists, create an All Pages trigger (or Initialization)
if not all_pages_trigger_id:
    print("Creating 'All Pages' trigger...")
    new_trigger = {
        'name': 'Initialization - All Pages',
        'type': 'init'  # Initialization trigger fires before regular page views
    }
    try:
        created_tr = service.accounts().containers().workspaces().triggers().create(
            parent=parent, body=new_trigger
        ).execute()
        all_pages_trigger_id = created_tr['triggerId']
        print(f"Created Trigger: {created_tr['name']} (ID: {all_pages_trigger_id})")
    except Exception as e:
        print(f"Init trigger failed: {e}. Trying standard pageview trigger...")
        new_trigger = {
            'name': 'All Pages',
            'type': 'pageview'
        }
        created_tr = service.accounts().containers().workspaces().triggers().create(
            parent=parent, body=new_trigger
        ).execute()
        all_pages_trigger_id = created_tr['triggerId']
        print(f"Created Trigger: {created_tr['name']} (ID: {all_pages_trigger_id})")

# 3. Create Google Tag (GA4 Configuration)
# Try 'googtag' first
tag_body = {
    'name': 'Google Tag - GA4 - G-3QBPY87VPP',
    'type': 'googtag',
    'parameter': [
        {
            'type': 'template',
            'key': 'tagId',
            'value': 'G-3QBPY87VPP'
        }
    ],
    'firingTriggerId': [all_pages_trigger_id]
}

try:
    print("Creating Google Tag (type: googtag)...")
    created_tag = service.accounts().containers().workspaces().tags().create(
        parent=parent, body=tag_body
    ).execute()
    print(f"SUCCESS: Created Tag: {created_tag['name']} (ID: {created_tag['tagId']})")
except Exception as e:
    print(f"Failed with googtag ({e}). Trying 'gaawc' (GA4 Configuration)...")
    tag_body['type'] = 'gaawc'
    tag_body['name'] = 'GA4 - Configuration - G-3QBPY87VPP'
    tag_body['parameter'] = [
        {
            'type': 'template',
            'key': 'measurementId',
            'value': 'G-3QBPY87VPP'
        }
    ]
    created_tag = service.accounts().containers().workspaces().tags().create(
        parent=parent, body=tag_body
    ).execute()
    print(f"SUCCESS: Created Tag: {created_tag['name']} (ID: {created_tag['tagId']})")

# 4. Create Version and Publish
print("\nCreating Version...")
version_body = {
    'name': 'v1: GA4 Google Tag Setup (G-3QBPY87VPP)',
    'notes': 'Migrated GA4 tracking from hardcoded gtag.js to GTM Google Tag.'
}
created_version = service.accounts().containers().workspaces().create_version(
    path=parent, body=version_body
).execute()

container_version = created_version.get('containerVersion')
version_id = container_version.get('containerVersionId')
print(f"Created Container Version ID: {version_id} ({container_version.get('name')})")

print("\nPublishing Container Version...")
version_path = f"accounts/6004690865/containers/265349373/versions/{version_id}"
published_version = service.accounts().containers().versions().publish(path=version_path).execute()
print(f"SUCCESS: Published Container Version: {published_version.get('containerVersion', {}).get('name')}!")
