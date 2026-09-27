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

# List workspaces
workspaces = service.accounts().containers().workspaces().list(parent=parent).execute().get('workspace', [])
print(f"Workspaces ({len(workspaces)}):")
default_ws = workspaces[0] if workspaces else None

if default_ws:
    ws_parent = f"{parent}/workspaces/{default_ws['workspaceId']}"
    print(f"Default Workspace: {default_ws['name']} (ID: {default_ws['workspaceId']})")
    
    # List tags
    tags = service.accounts().containers().workspaces().tags().list(parent=ws_parent).execute().get('tag', [])
    print(f"\nTags ({len(tags)}):")
    for t in tags:
        print(f"  - [{t.get('type')}] {t.get('name')} (ID: {t.get('tagId')})")
        
    # List triggers
    triggers = service.accounts().containers().workspaces().triggers().list(parent=ws_parent).execute().get('trigger', [])
    print(f"\nTriggers ({len(triggers)}):")
    for tr in triggers:
        print(f"  - [{tr.get('type')}] {tr.get('name')} (ID: {tr.get('triggerId')})")
        
    # List variables
    variables = service.accounts().containers().workspaces().variables().list(parent=ws_parent).execute().get('variable', [])
    print(f"\nVariables ({len(variables)}):")
    for v in variables:
        print(f"  - [{v.get('type')}] {v.get('name')} (ID: {v.get('variableId')})")
