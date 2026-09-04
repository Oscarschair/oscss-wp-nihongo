# oscss-wp-nihongo プロジェクト個別ルール & 憲章

本リポジトリは、日本語Webサイト向けに最適化されたモダンで保守性の高いWordPressカスタムテーマ「oscss-wp-nihongo」のコードベースです。

---

## 📜 プロジェクト開発・ドキュメント運用憲章

1. **第 1 条: 正本はコード (Code is Single Source of Truth)**
   テーマテンプレート（`.php`）、スタイル（`assets/css/`）、およびスクリプト（`assets/js/`）が常に一次情報（正本）である。
2. **第 2 条: ドキュメントは「なぜ」と「不変条件」に特化する (Document the "Why" and Invariants)**
   ドキュメントには「日本語組版・タイポグラフィの設計思想」「PHPモジュール分離の理由」「セキュリティ・エスケープ規約」を記述する。
3. **第 3 条: PR 同梱の同時更新 ＆ 日本語記述 (Definition of Done & Japanese PR)**
   機能追加・テンプレート改修時は、対応する `docs/` 配下の仕様書およびADRの更新を必須とし、PRは日本語で記述する。
4. **第 4 条: アーキテクチャ変更の ADR 記録義務 (Mandatory ADR Trail)**
   新しいフック体系の導入やCSS/JSビルドパイプラインの変更等は `docs/adr/` に記録する。

---

## 🛠️ テーマ設計・実装規約

### 1. PHPモジュラーアーキテクチャ
- `functions.php` にすべての処理を記述せず、必ず `functions/` ディレクトリ配下に責務ごとに分割する。
  - `functions/action.php`: アクションフック（エンキュー、テーマセットアップ等）
  - `functions/filter.php`: フィルターフック（抜粋、タイトル、クラス制御等）
  - `functions/shortcode.php`: ショートコード定義
  - `functions/utility.php`: 共通ヘルパー関数
- すべてのカスタム関数には `oscss_` プレフィックスを付与する。
- テンプレート内の動的出力には必ず適切なエスケープ（`esc_html()`, `esc_attr()`, `esc_url()` 等）を施す。

### 2. UI/UX ＆ 日本語タイポグラフィ設計
- 8pt Gridシステム（8px, 16px, 24px, 32px, 48px, 64px, 96px）による余白設計。
- 日本語フォントスタックの最適化（Hiragino Sans, Yu Gothic, Noto Sans JP 等）。
- 読みやすい行高（`line-height: 1.75`）と適切な文字送り（`letter-spacing: 0.03em`）。
- BEM命名規則によるコンポーネント指向CSS。
