# -*- coding: utf-8 -*-
import datetime
import json
import sys
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

# 1. ページ別パフォーマンス
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

# 2. クエリ別
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

# Markdownレポート作成
md_lines = []
md_lines.append(f"# 📊 Google Search Console 検索パフォーマンス分析レポート")
md_lines.append(f"- **対象ドメイン**: `sc-domain:oscarchair.jp` (絞り込み: `nihongo.oscarchair.jp`)")
md_lines.append(f"- **対象期間**: {start_date} 〜 {end_date} (直近90日間)\n")

# 合計メトリクス
total_clicks = sum(r.get("clicks", 0) for r in page_rows)
total_impressions = sum(r.get("impressions", 0) for r in page_rows)
avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0

md_lines.append("## 1. 全体サマリー（直近90日）")
md_lines.append(f"- **総クリック数**: {total_clicks:,} 回")
md_lines.append(f"- **総表示回数 (Impressions)**: {total_impressions:,} 回")
md_lines.append(f"- **平均CTR**: {avg_ctr:.2f}%")
md_lines.append(f"- **インデックス・検索露出ページ数**: {len(page_rows)} URL\n")

md_lines.append("## 2. トップ流入ページ・露出ランキング (Top Pages)")
md_lines.append("| ページURL / 記事 | クリック数 | 表示回数 | CTR | 平均掲載順位 |")
md_lines.append("| :--- | :---: | :---: | :---: | :---: |")

for r in sorted(page_rows, key=lambda x: (x.get("clicks", 0), x.get("impressions", 0)), reverse=True)[:15]:
    url = r["keys"][0].replace("https://nihongo.oscarchair.jp", "")
    if not url: url = "/"
    clicks = r.get("clicks", 0)
    imp = r.get("impressions", 0)
    ctr = r.get("ctr", 0) * 100
    pos = r.get("position", 0)
    md_lines.append(f"| `{url}` | **{clicks}** | {imp:,} | {ctr:.2f}% | **{pos:.1f}位** |")

md_lines.append("\n## 3. 主要検索クエリ・キーワードランキング (Top Queries)")
md_lines.append("| 検索キーワード (Query) | クリック数 | 表示回数 | CTR | 平均掲載順位 |")
md_lines.append("| :--- | :---: | :---: | :---: | :---: |")

for r in sorted(query_rows, key=lambda x: (x.get("clicks", 0), x.get("impressions", 0)), reverse=True)[:20]:
    q = r["keys"][0]
    clicks = r.get("clicks", 0)
    imp = r.get("impressions", 0)
    ctr = r.get("ctr", 0) * 100
    pos = r.get("position", 0)
    md_lines.append(f"| **{q}** | **{clicks}** | {imp:,} | {ctr:.2f}% | **{pos:.1f}位** |")

report_text = "\n".join(md_lines)

with open("scripts/search_console_report.md", "w", encoding="utf-8") as f:
    f.write(report_text)

print("Report generated at scripts/search_console_report.md")
