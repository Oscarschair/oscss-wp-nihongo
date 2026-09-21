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

# 直近28日間の日付範囲を算出 (Search Consoleは通常2〜3日遅れる)
today = datetime.date.today()
end_date = today - datetime.timedelta(days=2)
start_date = end_date - datetime.timedelta(days=28)

print(f"Fetching Search Analytics for {site_url} from {start_date} to {end_date}...")

# 1. サブドメイン nihongo.oscarchair.jp に絞り込んだ検索パフォーマンス
request_nihongo = {
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
    "rowLimit": 25
}

response_nihongo = service.searchanalytics().query(siteUrl=site_url, body=request_nihongo).execute()

# 2. ページ別のパフォーマンス (nihongo.oscarchair.jp)
request_pages = {
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
    "rowLimit": 25
}

response_pages = service.searchanalytics().query(siteUrl=site_url, body=request_pages).execute()

# 3. 全体（oscarchair.jp全体）のトップクエリ
request_overall = {
    "startDate": str(start_date),
    "endDate": str(end_date),
    "dimensions": ["query"],
    "rowLimit": 20
}

response_overall = service.searchanalytics().query(siteUrl=site_url, body=request_overall).execute()

# 4. 全体の合計サマリー (日付別)
request_totals = {
    "startDate": str(start_date),
    "endDate": str(end_date),
    "dimensions": ["date"],
}
response_totals = service.searchanalytics().query(siteUrl=site_url, body=request_totals).execute()

output_data = {
    "period": f"{start_date} to {end_date}",
    "nihongo_queries": response_nihongo.get("rows", []),
    "nihongo_pages": response_pages.get("rows", []),
    "overall_queries": response_overall.get("rows", []),
    "daily_totals": response_totals.get("rows", [])
}

print(json.dumps(output_data, ensure_ascii=False, indent=2))
