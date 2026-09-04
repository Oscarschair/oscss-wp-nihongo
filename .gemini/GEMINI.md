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

---

## 🔍 SEO専門レビュー ＆ 投稿ライフサイクルフック (Mandatory SEO Hooks)

新規記事の作成・保存時（`post_file_save`）およびWordPressへの投稿・公開前（`pre_post_publish`）には、[`.gemini/skills/seo-reviewer/SKILL.md`](file:///c:/Users/user/git/oscss-wp-nihongo/.gemini/skills/seo-reviewer/SKILL.md) が自動発動し、以下の10大SEO品質ゲートを通過することを必須とします：

1. **Title Tag**: 30〜60文字以内、主要検索キーワードを前方に配置、クリック率を高めるフック。
2. **Meta Description**: 100〜140文字程度で記事要約と読者ベネフィットを明記。
3. **見出し階層**: `<h1>` はタイトル1つのみ、本文内は `<h2>` ➔ `<h3>` の階層順序を厳守。
4. **リード文 ＆ BLUF**: 冒頭で「この記事でわかること」「テーマの結論」を明確に提示。
5. **検索意図・深掘り**: 学習者・異文化理解層の疑問に100%回答し、文化的背景・理由を解説。
6. **リッチコンテンツ**: 会話形式ダイアログ、比較テーブル、箇条書きを活用したスキャナビリティ。
7. **内部リンク**: 連載カテゴリー内の関連記事への適切なリンク導線。
8. **画像・Alt属性**: すべての画像に具体的な日本語 `alt` 属性を設定、16:9比率。
9. **E-E-A-T ＆ トーン**: 主人公オスカーの親しみやすく知的なトーンの一貫性。
10. **URLスラッグ**: 英数字ハイフン区切りのクリーンなスラッグ設計。

---

## 🎨 サムネイル一貫性 ＆ 投稿ライフサイクルフック (Mandatory Hooks)

記事の投稿・作成時には、[`.gemini/skills/thumbnail-consistency-agent/SKILL.md`](file:///c:/Users/user/git/oscss-wp-nihongo/.gemini/skills/thumbnail-consistency-agent/SKILL.md) が自動発動（`pre_post_publish` / `post_file_save`）し、以下の品質ゲートを通過することを必須条件とします：

1. **主人公「オスカー」の登場必須（公式モデル原型: `assets/images/hero-oscar-v2.png` / `https://nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/hero-oscar-v2.png`）**:
   - ふんわり茶髪マッシュ、大きめの黒縁丸メガネ、水色スウェット、知的な好青年。
   - **腕と手は必ず「左右2本のみ」**（AI特有の腕3本等の奇形を100%排除）。
   - **表情・ポーズの多様性**: 毎回同じ固定ポーズではなく、記事のシチュエーションに応じた自然なリアクション・驚き・発見・考察ポーズ（指差し、つり革キョロキョロ、首傾げ等）。
2. **カテゴリー別デザイン形式の維持**:
   - 🔍 **くらべてみました**: 左右分割のVS対比構図、2色のコントラストパステル背景。
   - 🗣️ **ことばのあや**: 会話吹き出し、ひらめき電球、優しいパステルラベンダー背景。
   - 🌏 **カルチャーショック**: 状況に応じた自然な驚き・発見リアクション、対比アイテム、明るいオレンジ/スカイブルー背景。
3. **共通フォーマット**:
   - 16:9比率、ポップで読みやすい日本語タイトル文字配置、アニメ・ベクターイラスト調。



