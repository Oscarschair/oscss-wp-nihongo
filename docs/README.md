# oscss-wp-nihongo ドキュメント

本ディレクトリは、WordPressカスタムテーマ「oscss-wp-nihongo」の設計書・運用手順・意思決定ログ（ADR）・機能仕様を管理するドキュメント階層です。

---

## 📚 ドキュメント構成一覧

| ドキュメント | 概要 | リンク |
| :--- | :--- | :--- |
| **全体アーキテクチャ** | テンプレート階層、PHPモジュール構造、CSS/JSアーキテクチャ | [architecture.md](file:///c:/Users/user/git/oscss-wp-nihongo/docs/architecture.md) |
| **デプロイ・環境構築手順** | テーマのインストール、有効化、更新、ローカル開発手順 | [deployment.md](file:///c:/Users/user/git/oscss-wp-nihongo/docs/deployment.md) |
| **機能・テンプレート仕様書** | 各テンプレート・コンポーネント・ショートコードの詳細仕様 | [domains/theme-spec.md](file:///c:/Users/user/git/oscss-wp-nihongo/docs/domains/theme-spec.md) |
| **投稿タイトル規格ガイドライン** | カテゴリー名プレフィックス必須化・表記揺れ防止ルール | [domains/post-title-guidelines.md](file:///c:/Users/user/git/oscss-wp-nihongo/docs/domains/post-title-guidelines.md) |
| **ADR（意思決定ログ）** | 設計判断・技術選定の経緯記録 | [adr/](file:///c:/Users/user/git/oscss-wp-nihongo/docs/adr/) |
| **運用・障害対応手順書** | キャッシュ管理、日常保守、トラブルシューティング | [ops/](file:///c:/Users/user/git/oscss-wp-nihongo/docs/ops/) |

### 📝 主な Architecture Decision Records (ADR)
- [0001: テーマ基本アーキテクチャ設計](file:///c:/Users/user/git/oscss-wp-nihongo/docs/adr/0001-theme-architecture.md)
- [0002: SEOモジュラーリファクタリング](file:///c:/Users/user/git/oscss-wp-nihongo/docs/adr/0002-seo-modular-refactoring.md)
- [0003: 外国人学習者向け全記事・全漢字へのHTML5ルビ（<ruby><rt>）標準適用方針](file:///c:/Users/user/git/oscss-wp-nihongo/docs/adr/0003-universal-kanji-ruby-policy.md)
- [0004: 投稿タイトルのカテゴリー名プレフィックス必須化および表記統一](file:///c:/Users/user/git/oscss-wp-nihongo/docs/adr/0004-post-title-category-prefix-standardization.md)

---

## 📜 プロジェクト開発・ドキュメント運用憲章 4 大原則
1. **第 1 条: 正本はコード (Code is Single Source of Truth)**
   ソースコードおよびテンプレートが常に一次情報（正本）である。
2. **第 2 条: ドキュメントは「なぜ」と「不変条件」に特化する (Document the "Why" and Invariants)**
   ビジネス背景、日本語組版思想、モジュール分離の根拠に特化する。
3. **第 3 条: PR 同梱の同時更新 ＆ 日本語記述 (Definition of Done & Japanese PR)**
   機能改修時はドキュメント更新を必須とし、PRは日本語で記述する。
4. **第 4 条: アーキテクチャ変更の ADR 記録義務 (Mandatory ADR Trail)**
   重要な設計決定は必ずADR（`docs/adr/NNNN-<title>.md`）として記録する。
