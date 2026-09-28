# 記事表示・セクション管理・広告制御標準仕様書 (Article Display & Ad Standards)

- **初版作成**: 2026-09-28
- **最新改定**: 2026-09-28
- **対象ファイル**: `functions/filter.php`, `assets/css/main.css`, `assets/js/main.js`, `single.php`, `content/posts/*.md`

---

## 1. 記事本文のセクション構造化仕様 (Section Wrapping Standard)

### 1.1 背景と設計思想
記事本文は、単なるフラットな段落の連続ではなく、「見出し＋その解説・会話劇」を1つの完結した論理単位（章）として管理します。
これにより、セマンティックなHTML構造を実現し、CSSスタイリングや広告挿入制御をセクション単位で厳密に適用します。

### 1.2 自動分割・ラップ仕様 ([functions/filter.php](file:///c:/Users/user/git/oscss-wp-nihongo/functions/filter.php))
`the_content` フィルターフック内の `oscss_wrap_and_protect_entry_sections()` により、以下のルールで自動的に `<section>` タグが生成されます：

```
[記事本文]
├── リード文（導入会話劇・概要） ➔ <section class="c-entry__section c-entry__section--lead ...">
├── 第1章（<h2>見出し ＋ 内容） ➔ <section class="c-entry__section ...">
├── 第2章（<h2>見出し ＋ 内容） ➔ <section class="c-entry__section ...">
├── ...
└── 今回の語彙（.c-vocab-box）  ➔ <section class="c-entry__section c-entry__section--vocab ...">
```

- **セクション要素の属性仕様**:
  ```html
  <section class="c-entry__section google-anno-skip no-ads adsbygoogle-noab" data-ad-exclude="true">
  ```

---

## 2. セクション内部広告の完全遮断仕様 (In-Section Ad Exclusion)

### 2.1 三重防御アーキテクチャ
セクションタグの内部には、いかなる AdSense 広告・スポンサーリンクの表示・自動挿入も許可しません。

| レイヤー | 実装箇所 | 遮断メカニズム |
| :--- | :--- | :--- |
| **HTML / クローラー** | `functions/filter.php` | `data-ad-exclude="true"`, `google-anno-skip`, `no-ads`, `adsbygoogle-noab` を付与し、広告エンジンのクローラーに対して挿入禁止を明示 |
| **CSS（物理非表示）** | `assets/css/main.css` | `.c-entry__section ins.adsbygoogle`, `.c-entry__section .google-auto-placed` などを `display: none !important; height: 0 !important;` で即時無効化 |
| **JavaScript（動的排除）**| `assets/js/main.js` | `MutationObserver`（`initAdSenseSectionGuard()`）が、DOMに追加されたセクション内の広告要素を検知し即座に `remove()` |

### 2.2 デバイス別レイアウト規約（PC / SP）
- **PC（1280px以上）**:
  - 本文エリアの両側（左右サイドバー）は広告配置 **許可（OK）**。
- **SP / スマートフォン（375px〜414px）**:
  - 画面幅が狭いため、両側サイドバー広告および本文内割り込み広告は **完全禁止（非表示保証）**。
  - 記事の上部・下部の正規広告枠のみを許可し、横スクロールはみ出し・誤タップを100%遮断する。

---

## 3. 「今回の語彙」カードBOX正本仕様 (Vocabulary Component Spec)

### 3.1 正本フォーマット
- **正本はローカルMarkdown内のHTMLブロック**:
  - 本文末尾に `<div class="c-vocab-box">` として完全なHTMLで記述する。
- **手書きマークダウン箇条書き（`* **単語**`）の完全禁止**:
  - 箇条書きリストとカードBOXの二重化を防ぐため、マークダウンの箇条書き形式での語彙記述は厳禁とする。
- **構造規格**:
  ```html
  <div class="c-vocab-box">
    <h3 class="c-vocab-box__title">🎯 今回の語彙（重要ボキャブラリー）</h3>
    <p class="c-vocab-box__lead">この学習ノートに登場した、覚えておきたい重要日本語：</p>
    <div class="c-vocab-grid">
      <div class="c-vocab-card">
        <div class="c-vocab-card__header">
          <span class="c-vocab-card__word">単語（よみ）</span>
          <span class="c-badge c-badge--jlpt c-badge--jlpt-n2">JLPT N2</span>
        </div>
        <p class="c-vocab-card__meaning"><strong>意味：</strong>英語解説</p>
        <p class="c-vocab-card__example"><strong>例文：</strong>日本語例文</p>
      </div>
    </div>
  </div>
  ```

---

## 4. 記事ボリューム ＆ 読了目安時間標準 (Reading Time Standard)

- **読了目安時間の計算式 ([functions/utility.php](file:///c:/Users/user/git/oscss-wp-nihongo/functions/utility.php))**:
  - `ceil(本文文字数 / 500)` 分（日本語 500文字/分 基準）。
  - ルビのふりがな（`<rt>〜</rt>`）は本文文字数の二重カウント防止のため自動除外。
- **ボリューム基準**:
  - **目安 7〜9分前後（3,500〜4,200文字規模）** を標準とする。
  - **2〜5分の短小記事は本番への掲載・公開を完全禁止**とする。

---

## 5. 全漢字HTML5安全ルビ標準 (Universal Safe Ruby Standard)

- **ADR 0003 準拠**:
  - 記事タイトル（frontmatter の `title:`）にはルビを振らず、プレーンテキストとする。
  - 本文中のすべての漢字に `<ruby>漢字<rt>ふりがな</rt></ruby>` を付与する。
  - 送り仮名・カタカナ・アルファベットは `<ruby>` の外側に完全に分離する（例: `<ruby>太<rt>ふと</rt></ruby>る`）。
