# 0006: 記事本文の見出し単位<section>分割管理および内部広告完全遮断方針

- **日付**: 2026-09-28
- **ステータス**: 承認済み (Accepted)
- **決定者**: プロダクトオーナー・開発チーム
- **対象**: `functions/filter.php`, `assets/css/main.css`, `assets/js/main.js`, `single.php`, `docs/domains/article-display-and-ad-standards.md`

---

## コンテキスト (Context)

「オスカーの日本語学習帳」において、Google AdSense の自動広告（Auto Ads）が記事本文内の不適切な位置（見出しの直下、会話劇ダイアログの間、語彙カード内）に無差別に挿入され、以下の重大な問題を引き起こしていた：

1. **学習UXの著しい低下**:
   - 会話劇や解説の文脈が広告によって分断され、外国人読者が日本語の学習・読解に集中できない。
   - スクロールするたびに全画面広告やインライン広告が割り込み、読書テンポが破壊される。
2. **マークアップ構造の不透明性**:
   - 記事本文がフラットな段落・見出しの羅列になっており、コンテンツの論理的ブロック（見出し＋その内容）の境界がブラウザや広告クローラーから識別できない。
3. **誤タップと視覚ノイズの増大**:
   - スマートフォン（SP）閲覧時において、小さな画面幅（375px）でコンテンツと広告が密集し、誤タップを誘発。

---

## 決定事項 (Decision)

記事本文の構造的完全性と、学習に集中できる高品質な読書環境を保証するため、以下の「セクション分割 ＆ 内部広告完全遮断アーキテクチャ」を正式策定・適用する。

### 1. 見出し＋内容単位での `<section>` 自動分割・管理
記事本文（`the_content`）が出力される際、[`functions/filter.php`](file:///c:/Users/user/git/oscss-wp-nihongo/functions/filter.php) の `oscss_wrap_and_protect_entry_sections()` により、各見出し（`<h2>`）および語彙ボックス（`.c-vocab-box`）の境界で自動的にコンテンツを分割し、以下のクラスと属性を持つ `<section>` タグで包括する：

```html
<section class="c-entry__section google-anno-skip no-ads adsbygoogle-noab" data-ad-exclude="true">
  <h2 class="wp-block-heading">見出しテキスト</h2>
  <p>見出し配下のコンテンツ・会話劇・解説文...</p>
</section>
```

### 2. セクションタグ内部の広告完全遮断（HTML/CSS/JS 三重防御）
`<section class="c-entry__section">` の内部には、Google AdSense 広告（自動広告・インライン広告・オーバーレイ広告）の表示・挿入を一切許可しない。

1. **HTML/クローラー層（除外シグナル）**:
   - `google-anno-skip`, `no-ads`, `adsbygoogle-noab` クラスの付与。
   - `data-ad-exclude="true"` 属性による明示的な広告挿入除外指示。
2. **CSSレイヤー（物理的完全非表示）**:
   - [assets/css/main.css](file:///c:/Users/user/git/oscss-wp-nihongo/assets/css/main.css) において、`.c-entry__section` 配下に挿入されたすべての AdSense 要素（`ins.adsbygoogle`, `.google-auto-placed`, `iframe[id*="google"]` 等）を `display: none !important; height: 0 !important;` で即時無効化。
3. **JS動的監視レイヤー（DOM即時排除）**:
   - [assets/js/main.js](file:///c:/Users/user/git/oscss-wp-nihongo/assets/js/main.js) の `initAdSenseSectionGuard()` において、`MutationObserver` を常時稼働させ、`.c-entry__section` 内に動的注入された広告ノードをミリ秒単位で検知・即時 `remove()` 排除。

### 3. PC / SP デバイス別広告配置ルール
- **PC（1280px以上）**:
  - 記事本文の両側（サイドバー・記事外エリア）への広告配置は許可。読書の邪魔にならない余白エリアを収益化に活用。
- **SP（375px〜414px）**:
  - スマートフォン表示時は、両側・本文内の割り込み広告を完全排除し、記事の上部・下部の正規広告枠のみに限定。横スクロールや誤タップを完全に防ぐ。

---

## 影響・結果 (Consequences)

### メリット (Positive)
- **読書体験の劇的向上**: 記事本文が美しい論理ブロック（見出し＋内容）としてセクション化され、本文中の不快な広告割り込みがゼロになる。
- **セマンティックWeb・アクセシビリティの向上**: 各章が `<section>` で構造化され、スクリーンリーダーや検索エンジンが記事の章立てを正確に把握可能。
- **安全な収益化**: 本文を保護しつつ、PCサイドバー等の安全なエリアでのみ広告を運用可能。

### デメリット・トレードオフ (Negative)
- セクション内部への広告挿入が禁止されるため、ページ全体のインプレッション数は減少するが、ユーザー滞在時間（読了率・エンゲージメント）の向上によって長期的なメディア価値を最大化する。
