# ADR 0002: SEOモジュール新設とテーマ全体リファクタリング

- **ステータス**: 承認済 (Accepted)
- **決定日**: 2026-09-09
- **対象コンポーネント**: `functions/seo.php`, `functions/utility.php`, `header.php`, `footer.php`, `front-page.php`, `single.php`, `404.php`, `template-parts/`

---

## 1. 背景と課題 (Context)
これまで「oscss-wp-nihongo」テーマは基本的な表示機能・閲覧数カウントを備えていたが、以下のSEO・アーキテクチャ上の課題が存在していた：
1. **メタタグ・OGP・構造化データの欠落**: 記事詳細やアーカイブ等で Meta Description、Canonical URL、OGP、Twitter Cards、JSON-LD（`BlogPosting`, `WebSite`, `BreadcrumbList`）が生成されていなかった。
2. **見出し階層（Heading Hierarchy）の乱れ**: フッターに `<h2>` が使われており、ページ全体の `h1` ➔ `h2` ➔ `h3` の厳格な階層構造と衝突していた。また、一部のMarkdown記事本文に `# タイトル` が重複していた。
3. **連載カテゴリーURLのハードコード**: 各テンプレートでカテゴリースラッグやURLの取得ロジックが分散・ハードコードされていた。

---

## 2. 決定事項 (Decision)
1. **`functions/seo.php` の新設**:
   - Meta Description / Robots / Canonical URL の自動動的生成。
   - OGP / Twitter Cards（`summary_large_image`）の完全対応。
   - Google リッチリザルトおよび AI 検索（LLMO）に最適化された JSON-LD 構造化データの自動出力。
   - Google Fonts preconnect および不要なWordPressデフォルトヘッダー/Emojiの無効化。
2. **PHPモジュラーアーキテクチャとヘルパーの共通化**:
   - `oscss_get_series_categories()` / `oscss_get_series_category_url()` による連載カテゴリーURL解決の一元化。
   - 記事読了目安時間算出ヘルパー `oscss_get_reading_time()` の導入。
   - プレーンテキスト要約クレンジング `oscss_get_clean_excerpt()` の導入。
3. **テンプレートマークアップとセマンティクスの是正**:
   - フッターの `<h2>` を `<div>` へ変更し見出し階層を正常化。
   - Markdown記事の本文冒頭から不要なH1見出しを除去し、全11記事のSEO 10大基準チェック（`scripts/audit_seo_posts.py`）を 100% PASS化。

---

## 3. 結果・影響 (Consequences)
- **ポジティブな影響**:
  - Google および AI 検索エンジンに対するインデックス品質・リッチリザルト表示・CTRが大幅に向上。
  - 不要タグ削除とPreconnectにより Core Web Vitals (FCP / LCP) が高速化。
  - コードの重複が解消され、保守性・拡張性が大幅に向上。
- **トレードオフ・注意点**:
  - 新規記事追加時は `scripts/audit_seo_posts.py` による自動品質チェックを継続適用する。
