# 重要語彙コンポーネント仕様書 (Vocabulary Component Specification)

本ドキュメントは、「オスカーの日本語学習帳」における記事末尾の「今回の語彙（重要ボキャブラリー）」セクションのコンポーネント設計・HTML構造・CSSスタイル・運用ルールを定義します。

---

## 1. 概要と目的
各記事で登場した重要な日本語（JLPT N5〜N1対応）を、学習者が一目で直感的に復習できるように、単なるテキスト箇条書きではなく**カード型UI（`.c-vocab-card`）およびグリッド（`.c-vocab-grid`）**で美しく提示します。

---

## 2. 正本HTML構造 (Canonical HTML Structure)

WordPressの投稿本文内では、必ず以下の Gutenberg HTMLブロック（`<!-- wp:html -->`）として保存します：

```html
<!-- wp:html -->
<div class="c-vocab-box">
  <h3 class="c-vocab-box__title">🎯 今回の語彙（重要ボキャブラリー）</h3>
  <p class="c-vocab-box__lead">この学習ノートに登場した、覚えておきたい重要日本語：</p>
  <div class="c-vocab-grid">
    <div class="c-vocab-card">
      <div class="c-vocab-card__header">
        <span class="c-vocab-card__word">店内（てんない）</span>
        <span class="c-badge c-badge--jlpt c-badge--jlpt-n3">JLPT N3</span>
      </div>
      <p class="c-vocab-card__meaning"><strong>意味：</strong>inside the shop</p>
      <p class="c-vocab-card__example"><strong>例文：</strong>「店内でお召し上がりですか、それともお持ち帰りですか」と聞かれた。</p>
    </div>
    <!-- 2枚目・3枚目のカードが続く -->
  </div>
</div>
<!-- /wp:html -->
```

---

## 3. スタイル定義 (`assets/css/main.css`)

- **`.c-vocab-box`**: 左端にプライマリーカラーの太線（`border-left: 5px solid var(--color-primary)`）を持つソフトなグラデーションボックス。
- **`.c-vocab-grid`**: CSS Grid によるレスポンシブ配置（`grid-template-columns: repeat(auto-fit, minmax(260px, 1fr))`）。PCでは横並び（3列等）、スマホでは自動的に1列縦並びにスタック。
- **`.c-vocab-card`**: 白背景、角丸、微弱シャドウ、ホバー時に浮き上がるインタラクション（`translateY(-2px)`）。
- **`.c-vocab-card__header`**: 単語（アクセントブルー・太字）とJLPTバッジが左右に美しく分かれるヘッダー。
- **`.c-vocab-card__example`**: 薄いグレー背景の角丸ボックスで、例文を分かりやすく囲み表示。

---

## 4. 運用上の不変条件 ＆ 先祖返り防止ルール (Invariants)

1. **Markdown箇条書きでの直接上書きの厳格禁止**:
   - ローカルの Markdown 原稿（`content/posts/*.md`）では可読性のためにリスト形式で記述されている場合でも、**WordPress本番へ同期する際は必ず `scripts/core/restore_all_vocab_boxes.py` を通して HTML カード形式へ変換して同期すること**。
   - プレーンな `<ul><li>` で WordPress に流し込む先祖返り事故を二度と起こさない。

2. **復元・保守スクリプト**:
   - マスターデータ: [`clean_master_vocab_boxes.json`](file:///c:/Users/user/git/oscss-wp-nihongo/clean_master_vocab_boxes.json)
   - 同期・復元スクリプト: [`scripts/core/restore_all_vocab_boxes.py`](file:///c:/Users/user/git/oscss-wp-nihongo/scripts/core/restore_all_vocab_boxes.py)
