# oscss-wp-nihongo

[![WordPress Theme](https://img.shields.io/badge/WordPress-Theme-21759B?logo=wordpress&logoColor=white)](https://wordpress.org/)
[![PHP Version](https://img.shields.io/badge/PHP-8.0%2B-777BB4?logo=php&logoColor=white)](https://www.php.net/)
[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](http://www.gnu.org/licenses/gpl-2.0.html)

日本語Webサイト向けにタイポグラフィ・視認性・保守性を極限まで高めた、モダンなWordPressカスタムテーマです。  
8pt Gridシステム、BEM設計によるCSS変数管理、およびPHPモジュラーアーキテクチャを採用しています。

---

## 🌟 主な特徴

- 🇯🇵 **日本語タイポグラフィの最適化**: `line-height: 1.75`、文字送り、美しいフォントスタック（Inter + Noto Sans JP）を標準搭載。
- 📐 **8pt Grid デザインシステム**: すべての余白・パディング・マージンを8の倍数で統一し、デバイスサイズを問わず破綻のないレイアウトを実現。
- 🧩 **モジュラーPHPアーキテクチャ**: `functions/` ディレクトリ配下に `action.php`, `filter.php`, `shortcode.php`, `utility.php` を分割配置し、コードの肥大化を完全防止。
- 📱 **レスポンシブ ＆ アクセシビリティ**: スマホ（SP）ハンバーガーメニュー、WCAG 4.5:1 超の高コントラスト、キーボード操作対応スキップリンク。
- ⚡ **軽量 ＆ 高速**: 外部依存フレームワークを排し、Vanilla CSS & JavaScript で高速表示。

---

## 📁 ディレクトリ構造

```
oscss-wp-nihongo/
├── .gemini/                         # Gemini AI エージェント開発ルール・憲章
│   └── GEMINI.md
├── docs/                            # プロジェクト設計・運用ドキュメント
│   ├── README.md                    # ドキュメント目次
│   ├── architecture.md              # テンプレート階層 & アーキテクチャ設計書
│   ├── deployment.md                # インストール・デプロイ手順書
│   ├── adr/                         # Architecture Decision Records
│   │   └── 0001-theme-architecture.md
│   └── domains/                     # テーマ機能仕様書
│       └── theme-spec.md
├── assets/                          # フロントエンド静的アセット
│   ├── css/
│   │   ├── tokens.css               # カラー・タイポグラフィ・余白変数
│   │   └── main.css                 # メインスタイルシート (BEM)
│   ├── js/
│   │   └── main.js                  # モバイルメニュー・UIスクリプト
│   └── images/
│       └── placeholder.svg          # アイキャッチフォールバック画像
├── functions/                       # PHPモジュラーロジック
│   ├── action.php                   # add_action フック
│   ├── filter.php                   # add_filter フック
│   ├── shortcode.php                # カスタムショートコード
│   └── utility.php                  # 共通ヘルパー関数
├── template-parts/                  # 分割テンプレートパーツ
│   ├── header-nav.php               # ヘッダーナビ
│   ├── post-card.php                # 記事一覧カード
│   └── pagination.php               # ページ送り
├── 404.php                          # 404 Not Found
├── archive.php                      # カテゴリ/タグアーカイブ
├── footer.php                       # グローバルフッター
├── front-page.php                   # トップページ
├── functions.php                    # モジュールローダー
├── header.php                       # グローバルヘッダー
├── index.php                        # メインフォールバック
├── page.php                         # 固定ページ
├── single.php                       # 投稿詳細
├── style.css                        # テーマメタ情報
├── screenshot.png                   # 管理画面テーマサムネイル
└── README.md                        # 本ファイル
```

---

## 🚀 クイックスタート

### インストールと有効化
1. 本フォルダを WordPress の `wp-content/themes/` ディレクトリ配下に配置します。
2. WordPress管理画面の **「外観」 > 「テーマ」** を開き、**「oscss-wp-nihongo」** を有効化します。
3. **「外観」 > 「メニュー」** より、作成したメニューを **「メインナビゲーション」** に設定します。

---

## 📖 ドキュメント一覧

- [全体アーキテクチャ設計書](file:///c:/Users/user/git/oscss-wp-nihongo/docs/architecture.md)
- [インストール・デプロイ手順書](file:///c:/Users/user/git/oscss-wp-nihongo/docs/deployment.md)
- [機能・テンプレート仕様書](file:///c:/Users/user/git/oscss-wp-nihongo/docs/domains/theme-spec.md)
- [ADR 0001: テーマアーキテクチャ選定](file:///c:/Users/user/git/oscss-wp-nihongo/docs/adr/0001-theme-architecture.md)

---

## 📄 ライセンス

本テーマは [GPL v2 or later](http://www.gnu.org/licenses/gpl-2.0.html) の下で公開されています。
