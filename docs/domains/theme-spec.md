# テーマ仕様書 (Theme Specification)

本ドキュメントでは、「oscss-wp-nihongo」テーマに含まれる各テンプレート、カスタム関数、ショートコード、およびUIコンポーネントの仕様を定義します。

---

## 1. テンプレート仕様

### 1.1 `front-page.php` (フロントページ)
- **ヒーローセクション**: サイトのメインキャッチコピー、サブタイトル、CTAボタン。
- **特徴セクション**: 3カラムの特徴/サービスカード表示。
- **最新記事セクション**: `WP_Query` を用いた最新の投稿（デフォルト6件）のグリッド表示。

### 1.2 `single.php` (個別投稿)
- **投稿ヘッダー**: タイトル、公開日・更新日、カテゴリーバッジ、アイキャッチ画像。
- **本文領域**: 日本語タイポグラフィ最適化（見出しh2〜h4装飾、引用、テーブル、リスト等）。
- **投稿フッター**: タグ一覧、前後の記事へのナビゲーションリンク。

### 1.3 `page.php` (固定ページ)
- **ページヘッダー**: ページタイトル。
- **本文領域**: リッチテキストコンテンツの適切なスタイリング。

### 1.4 `archive.php` (アーカイブ)
- **アーカイブヘッダー**: カテゴリー名/タグ名/年月および説明文。
- **記事一覧**: 記事カードのグリッドレイアウトとページネーション（`the_posts_pagination`）。

### 1.5 `404.php` (404 Not Found)
- 親切なメッセージとトップページへの導線リンク、サイト内検索フォーム。

---

## 2. カスタムショートコード (`functions/shortcode.php`)

| ショートコード | 引数 | 説明 |
| :--- | :--- | :--- |
| `[oscss_btn url="..." text="..."]` | `url`, `text`, `target`, `style` (primary/secondary) | モダンなCTAボタンを表示 |
| `[oscss_alert type="info"]...[/oscss_alert]` | `type` (info/warning/success) | 枠線付きのアラート・注目ボックスを表示 |

---

## 3. ヘルパー関数 (`functions/utility.php`)

| 関数名 | 戻り値 | 説明 |
| :--- | :--- | :--- |
| `oscss_get_post_thumbnail_url($size)` | `string` | 投稿のサムネイルURLまたはフォールバック画像URLを安全に取得 |
| `oscss_posted_on()` | `void` (HTML出力) | 公開日および更新日のフォーマット済みHTMLを出力 |
| `oscss_entry_category()` | `void` (HTML出力) | カテゴリーバッジ一覧を出力 |
| `oscss_breadcrumb()` | `void` (HTML出力) | 構造化されたパンくずリストを出力 |

---

## 4. タイポグラフィ・組版仕様（ルビースタイル）

外国人学習者向けに、記事本文内のすべての漢字に対してHTML5ルビタグ（`<ruby><rt>`）を標準適用する（詳細は [ADR 0003](file:///c:/Users/user/git/oscss-wp-nihongo/docs/adr/0003-universal-kanji-ruby-policy.md) 参照）。

### 4.1 組版ルール
- **漢字限定原則**: 送り仮名・接頭辞・カタカナ語にはルビを付与せず、純粋な漢字部分のみを `<ruby>` で囲む（例: `<ruby>太<rt>ふと</rt></ruby>る`、`お<ruby>冷<rt>ひや</rt></ruby>`、`<ruby>紙<rt>かみ</rt></ruby>エプロン`）。
- **カッコ読み行の廃止**: 漢字頭上へのルビ配置に伴い、文末や直下の重複ひらがな読み行（例: `（すみません、おひやは どこに ありますか？）`）は全廃する。

### 4.2 CSSスタイル仕様
```css
ruby {
	ruby-position: over;
	ruby-align: center;
	display: inline-ruby;
}

rt {
	font-size: 0.62em;
	color: var(--color-primary);
	font-weight: 600;
	letter-spacing: 0.02em;
	line-height: 1;
	user-select: none; /* コピペ時のルビ文字混入防止 */
}
```

---

## 5. ブランドロゴ ＆ 光学補正ファビコン仕様（[ADR 0008](file:///c:/Users/user/git/oscss-wp-nihongo/docs/adr/0008-airy-pastel-brand-logo-unification.md)）

サイト全体の淡彩パステルグラデーション（`#EEF2FF` → `#F5F3FF` → `#FFF1F2`）および手描き水彩イラストと調和する純粋ベクターブランドロゴを採用する。

| 用途 | アセットパス | 仕様・不変条件 |
| :--- | :--- | :--- |
| **ヘッダーロゴ（ライト背景）** | `assets/images/logo-lockup.svg` | 見開き学習帳×吹き出し×ベビー桜しおり（淡彩パステル維持） ＋ 高視認スレートブラック文字（主文字 `#0F172A` `wght=680` `17.85:1` AAA / 副文字 `#1E293B` `14.63:1` AAA）2段ミニマル構成。全グリフ `<path>` アウトライン済み（PC高 `48px` / SP高 `40px`）。 |
| **フッターロゴ（ダーク背景）** | `assets/images/logo-lockup-dark.svg` | ダークフッター（`#0f172a`）向けに白系高コントラスト文字（`#FFFFFF` / `#E2E8F0`）へ最適化した横組みSVGロゴ。 |
| **単体シンボル** | `assets/images/logo-symbol.svg` | `200×200` viewBox 単体ベクターシンボル。 |
| **構造化データ用ロゴ** | `assets/images/logo-organization.png` | JSON-LD `Organization.logo` 用の `512×512px` ラスタPNG（著者 `Person.image` は `x-profile-icon.png` を使用）。 |
| **サイトアイコン・ファビコン** | `favicon-512x512.png` / `192x192` / `apple-touch-icon.png` / `32x32` / `16x16` / `favicon.ico` | `32px` / `16px` / `ico` には縮小時の線消失を防ぐ **Optical Sizing（線幅 `7.0` 光学補正）** を適用。 |


