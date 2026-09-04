# テーマ・アーキテクチャ設計書 (Architecture Design)

本ドキュメントでは、WordPressカスタムテーマ「oscss-wp-nihongo」の全体構造、テンプレート階層、PHPモジュール設計、CSS/JSアーキテクチャについて解説します。

---

## 1. テンプレート階層 (Template Hierarchy)

WordPress標準のテンプレート階層に準拠し、関心の分離を徹底しています。

```
ルート/
├── front-page.php          # トップページ（ヒーローセクション、特徴、最新記事一覧等）
├── index.php               # フォールバックテンプレート
├── single.php              # 個別投稿記事詳細
├── page.php                # 固定ページ詳細
├── archive.php             # カテゴリー・タグ・日付アーカイブ
├── 404.php                 # 404エラーページ
├── header.php              # グローバルヘッダー（ナビゲーション含む）
├── footer.php              # グローバルフッター（コピーライト、ウィジェット等）
└── template-parts/         # 再利用可能なテンプレートパーツ
    ├── header-nav.php      # ナビゲーションメニュー
    ├── post-card.php       # 記事カードパーツ
    └── pagination.php      # ページ送りパーツ
```

---

## 2. PHPモジュラー構造 (`functions/`)

ルートの `functions.php` はモジュールローダーに徹し、処理の実体は `functions/` ディレクトリ配下に責務ごとに分離します。

```
functions/
├── action.php       # add_action フック（テーマ設定、スクリプト・スタイルエンキュー、メニュー登録）
├── filter.php       # add_filter フック（記事抜粋、タイトル整形、body_class 制御）
├── shortcode.php    # カスタムショートコード（CTAボタン、アラートボックス等）
└── utility.php      # 共通ユーティリティ関数（日付フォーマット、パンくずリスト、安全な抜粋生成等）
```

### 命名規則 & セキュリティ
- すべてのカスタム関数は `oscss_` プレフィックスを付与。
- HTML出力時は `esc_html()`, `esc_attr()`, `esc_url()` を徹底。

---

## 3. CSS & フロントエンド設計

### 3.1 設計思想
- **CSS変数（Design Tokens）**: `assets/css/tokens.css` でカラー、フォント、余白を一元管理。
- **8pt Gridシステム**: 余白・パディング・サイズを8の倍数で設計。
- **BEM命名規則**: `.c-card`, `.c-card__title`, `.c-card--featured` のように Block-Element-Modifier 形式を採用し、スタイルの衝突を防止。

### 3.2 日本語タイポグラフィ最適化
- 日本語フォントスタック: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Yu Gothic", "Meiryo", sans-serif`
- 行間（`line-height: 1.75`）、文字間（`letter-spacing: 0.03em`）の最適化。
- 見出しの折り返しとワードブレーク（`word-break: keep-all; overflow-wrap: anywhere;`）。
