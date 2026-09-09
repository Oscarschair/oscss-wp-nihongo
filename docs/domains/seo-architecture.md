# 🔍 SEO ＆ 構造化データ アーキテクチャ仕様書 (SEO Architecture)

本ドキュメントは、WordPressカスタムテーマ「oscss-wp-nihongo」におけるSEO最適化、OGP、Twitter Cards、JSON-LD（Schema.org）構造化データ、およびCore Web Vitalsパフォーマンス向上の設計仕様を定義します。

---

## 🏛️ アーキテクチャ概要

SEO機能は `functions/seo.php` に一元化され、WordPress標準のフックシステムを通じて `<head>` 内に最適なメタデータと構造化データを自動出力します。

```
functions/seo.php
├── oscss_seo_meta_tags()        # Meta Description, Canonical, Robots, OGP, Twitter Cards
├── oscss_seo_json_ld()          # JSON-LD 構造化データ（WebSite, BlogPosting, BreadcrumbList, Person）
├── oscss_seo_resource_hints()   # Preconnect, DNS-Prefetch
└── oscss_cleanup_wp_head()      # 不要タグ・Emojiの無効化（高速化）
```

---

## 📋 1. メタタグ ＆ OGP仕様

### 1.1 ページ種別ごとの動的生成ルール

| ページ種別 | Title Tag | Meta Description | Canonical URL | og:type | og:image |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **トップページ** | サイト名 \| キャッチフレーズ | 固定の高品質サイト説明文（約120字） | `https://nihongo.oscarchair.jp/` | `website` | `screenshot.png` (デフォルト) |
| **投稿詳細 (Single)** | 記事タイトル \| サイト名 | 記事抜粋 / 本文先頭120字（タグ・Markdown記号除去） | 記事の固定パーマリンク | `article` | 記事アイキャッチ画像 (1200x630) |
| **カテゴリー一覧** | カテゴリー名 の記事一覧 \| サイト名 | カテゴリー説明文（未設定時は動的生成文） | カテゴリーURL | `object` | `screenshot.png` |
| **タグ一覧** | #タグ名 の記事一覧 \| サイト名 | タグ説明文（未設定時は動的生成文） | タグURL | `object` | `screenshot.png` |
| **404 / 検索** | 該当エラー/検索タイトル \| サイト名 | 案内文（404/検索時は `noindex, follow` 付与） | 正規化URL | `website` | `screenshot.png` |

---

## 📊 2. JSON-LD 構造化データ仕様 (Schema.org)

Google リッチリザルトテストおよび AI 検索（LLMO）に完全対応した以下のスキーマを出力します：

1. **`BreadcrumbList` (全ページ共通)**
   - ホーム ➔ カテゴリー ➔ 記事タイトル の階層を正確に `itemListElement` 配列として構造化。
2. **`WebSite` (トップページ)**
   - `SearchAction` を内包し、Google 検索結果でのサイト内検索ボックスの表示に対応。
   - `Person`（車 浩文 / オスカー）を著者・発行者として紐付け。
3. **`BlogPosting` (記事詳細ページ)**
   - `headline`, `description`, `image`, `datePublished`, `dateModified`, `author` (Person), `publisher` (Organization), `articleSection`, `inLanguage` (ja) を完全装備。

---

## ⚡ 3. パフォーマンス ＆ Core Web Vitals 最適化

1. **リソースヒント (`preconnect` / `dns-prefetch`)**:
   - Google Fonts (`fonts.googleapis.com`, `fonts.gstatic.com`)
   - Google AdSense, GA4
2. **ファーストビュー画像の優先読込**:
   - ヒーロー画像および記事アイキャッチに `loading="eager"`, `fetchpriority="high"` を設定。
   - カード一覧・アバター・その他の画像には `loading="lazy"`, `decoding="async"` を徹底。
3. **クリーンアップ**:
   - `wp_generator`, `rsd_link`, `wlwmanifest_link`, `wp_shortlink_wp_head`, `feed_links` 等の不要なヘッダーメタを削除。
   - WordPress標準の Emoji スクリプト・インラインスタイルを無効化し、ページ描画ブロックを解消。
