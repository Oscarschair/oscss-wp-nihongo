import datetime
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

KEY_FILE = "C:/Users/user/.gemini/geminicode-490015-6b66a8432071.json"
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

credentials = service_account.Credentials.from_service_account_file(
    KEY_FILE, scopes=SCOPES
)
service = build("searchconsole", "v1", credentials=credentials)

site_url = "sc-domain:oscarchair.jp"

today = datetime.date.today()
end_date = today - datetime.timedelta(days=2)
start_date = end_date - datetime.timedelta(days=90)

print(f"=== Search Console Analysis for nihongo.oscarchair.jp ({start_date} ~ {end_date}) ===")

# 1. ページ別
req_pages = {
    "startDate": str(start_date),
    "endDate": str(end_date),
    "dimensions": ["page"],
    "dimensionFilterGroups": [
        {
            "filters": [
                {
                    "dimension": "page",
                    "operator": "contains",
                    "expression": "nihongo.oscarchair.jp"
                }
            ]
        }
    ],
    "rowLimit": 50
}
res_pages = service.searchanalytics().query(siteUrl=site_url, body=req_pages).execute()
page_rows = res_pages.get("rows", [])
print(f"\n[Page Performance] Found {len(page_rows)} pages:")
for r in page_rows:
    print(f"- {r['keys'][0]}")
    print(f"   Clicks: {r['clicks']} | Imp: {r['impressions']} | CTR: {r['ctr']:.2%} | Avg Pos: {r['position']:.1f}")

# 2. クエリ別（日本語サイトに流入した検索ワード）
req_queries = {
    "startDate": str(start_date),
    "endDate": str(end_date),
    "dimensions": ["query"],
    "dimensionFilterGroups": [
        {
            "filters": [
                {
                    "dimension": "page",
                    "operator": "contains",
                    "expression": "nihongo.oscarchair.jp"
                }
            ]
        }
    ],
    "rowLimit": 50
}
res_queries = service.searchanalytics().query(siteUrl=site_url, body=req_queries).execute()
query_rows = res_queries.get("rows", [])
print(f"\n[Search Queries for nihongo.oscarchair.jp] Found {len(query_rows)} queries:")
for r in query_rows:
    print(f"- \"{r['keys'][0]}\" -> Clicks: {r['clicks']}, Imp: {r['impressions']}, CTR: {r['ctr']:.2%}, Pos: {r['position']:.1f}")
