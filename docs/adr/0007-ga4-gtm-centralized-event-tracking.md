# 0007: GA4計測のGTM（GTM-K6NZHVDJ）一元管理化および直書きgtag.jsの廃止

- **日付**: 2026-11-18
- **ステータス**: 承認済み (Accepted)
- **決定者**: 開発チーム

## コンテキスト (Context)
これまで「オスカーの日本語学習帳（`nihongo.oscarchair.jp`）」では、`header.php` に Google Tag Manager（`GTM-K6NZHVDJ`）スニペットを設置しつつ、`functions/action.php` の `oscss_head_analytics_and_ads()` においても GA4（`G-3QBPY87VPP`）の `gtag.js` が直書き出力されていた。

今後、全漢字ふりがな（ルビ）ON/OFF切替（`ruby_toggle_click`）、記事読了（`cv_article_complete_read`）、カテゴリー・JLPT目安レベル絞り込み（`article_filter_click`）、Buy Me a Coffee 支援クリック（`cv_bmc_support_click`）、メインサイト送客（`cv_mainsite_click`）等の全19イベントおよびページグルーピング（`content_group` 全10区分）を GTM 経由で計測するにあたり、HTML直書きの `gtag.js` が残存していると `page_view` の二重計上や初期設定パラメータの競合が発生する課題があった。

## 決定事項 (Decision)
1. **直書き `gtag.js` の廃止と GTM 一元管理化**:
   - `functions/action.php` の `oscss_head_analytics_and_ads()` から直書き `gtag.js`（`G-3QBPY87VPP`）を削除し、`<head>` 直書きが必要な Google AdSense（`ca-pub-6358046201606104`）のみを維持する。
   - GA4 設定タグ（`GA4 - Configuration Tag`）および全カスタムイベント・ユーザープロパティの配信を `header.php` の `GTM-K6NZHVDJ` に完全一本化する。
2. **GA4 カスタム定義・GTM コンテナ定義のコード管理**:
   - GA4 プロパティ（`properties/354369646`）に登録したカスタムディメンション・カスタム指標・計算指標・キーイベントの正本データを `ga4/` ディレクトリ配下に JSON 形式で管理する。
   - GTM コンテナ（`GTM-K6NZHVDJ`）のインポート用コンテナ定義を `gtm/GTM.json` として管理する。
3. **未公開プレビュー・非本番アクセスの計測遮断**:
   - GTM 側の例外（ブロッキング）トリガーにより、WordPress 管理者ログイン中（`body.logged-in` / `admin-bar`）、プレビュー表示（`?preview=true`）、および本番ドメイン以外のアクセスが本番 GA4 レポートに混入しない不変条件を設ける（`debug_mode=1` / GTM Preview 検証時を除く）。

## 影響・結果 (Consequences)
### メリット (Positive)
- GTM と直書き `gtag.js` の二重初期化リスクを 100% 解消し、クリーンな単一計測パイプラインを実現できる。
- テーマ PHP コードを再デプロイすることなく、GTM 側で柔軟にイベント・パラメータ・オーディエンス条件を拡張・保守できる。
- `ga4/` および `gtm/` ディレクトリに API エクスポート JSON を保持することで、設定の監査性・再現性が担保される。

### デメリット・トレードオフ (Negative / Trade-offs)
- GTM コンテナ側で最新バージョン（`GA4 - Configuration Tag` 含む）が公開（Publish）されていることが計測稼働の前提条件となる。
