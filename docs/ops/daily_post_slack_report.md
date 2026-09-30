# 投稿予約数 Slack 日次レポート＆リマインダー運用手順書

## 1. 概要
本番環境 WordPress（`nihongo.oscarchair.jp`）の「公開予約（`future` ステータス）」記事の件数を毎日自動集計し、Slackへレポートします。
ストックが **10件以下** になった場合は、`@Hirofumi Kuruma` 宛てに記事作成リマインドをメンション付きで送信します。

---

## 2. 構成・アーキテクチャ

- **監視スクリプト**: [`scripts/report_scheduled_posts.py`](file:///c:/Users/user/git/oscss-wp-nihongo/scripts/report_scheduled_posts.py)
  - 本番サーバーへSSH経由で安全に接続し、DB内の `post_type='post' AND post_status='future'` の件数と公開予定日時・タイトルを取得。
  - 件数が 10件以下（`count <= 10`）の場合: 🚨 `@Hirofumi Kuruma` メンションを付与してリマインド。
  - 件数が 11件以上の場合: 🟢 正常稼働レポートとして予約一覧を通知。
- **定期実行タスク**: [`scripts/setup_daily_report_task.py`](file:///c:/Users/user/git/oscss-wp-nihongo/scripts/setup_daily_report_task.py)
  - Windows タスクスケジューラ名: `OSCSS_WP_Nihongo_Daily_Scheduled_Posts_Report`
  - 実行頻度: 毎日 朝 09:00（バックグラウンド `pythonw.exe` 実行）
- **通知先**: Slack チャンネル `#bot_antigravity_notice`（Incoming Webhook）

---

## 3. 手動実行・動作確認コマンド

```bash
# 1. コンソール表示のみ（Slackには送信しない）
python scripts/report_scheduled_posts.py --dry-run

# 2. アラート（メンション）のシミュレーション（閾値を20件に引き上げてテスト）
python scripts/report_scheduled_posts.py --dry-run --threshold 20

# 3. 即時 Slack 送信
python scripts/report_scheduled_posts.py

# 4. タスクスケジューラの実行時刻変更（例: 毎朝 08:30 に変更）
python scripts/setup_daily_report_task.py 08:30
```
