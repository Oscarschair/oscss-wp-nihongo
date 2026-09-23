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

## 🐝 SWARMエージェント編成 ＆ 役割分担 (Multi-Agent Swarm)
単一AIによる抱え込みを遮断し、以下の役割分担で運用します。

```
                 【ディレクター / ユーザー】
                            │ 指示
                            ▼
                  [WP-Supervisor]
          （WBS管理・進行管理・タスクディスパッチ）
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
  [Theme-Developer]     [Content-Writer]   [Thumbnail-Artist]
  ・PHPモジュール分離   ・日本語記事執筆   ・オスカー画像生成
  ・WordPressフック     ・No-Asterisk規約  ・16:9比率/パステル
         │                  │                  │
         └──────────────────┼──────────────────┘
                            ▼
                  [Red Team QA]（独立審査 / 差し戻し上限3回）
                  ・10大SEO品質ゲート審査（seo-reviewer）
                  ・サムネイル品質審査（image-reviewer）
                  ・PC（1280px+）/ SP（375px）画面崩れ検査
```

- **WP-Supervisor**: 全体進行、カテゴリー投稿バランス管理。
- **Theme-Developer**: `functions/` 配下のモジュール分割、エスケープ徹底。
- **Content-Writer**: 連載記事執筆、BLUF原則、`**` 禁止・HTMLタグ強調。
- **Thumbnail-Artist**: 主人公オスカー画像生成、多彩なポーズ切り替え。
- **Red Team QA**: SEO・画像・レイアウトの独立した客観的監査役。

---

## 🛠️ 利用可能・推奨グローバルスキル
本プロジェクトでは、以下のグローバルスキルを活用します：
- **WordPress・フロントエンド**: [`wordpress-theme-development`](file:///C:/Users/user/.gemini/config/skills/wordpress-theme-development/SKILL.md), [`wordpress-coding-standard`](file:///C:/Users/user/.gemini/config/skills/wordpress-coding-standard/SKILL.md), [`wordpress-uiux-design-standard`](file:///C:/Users/user/.gemini/config/skills/wordpress-uiux-design-standard/SKILL.md), [`php-modular-architecture`](file:///C:/Users/user/.gemini/config/skills/php-modular-architecture/SKILL.md)
- **品質レビュー**: [`seo-reviewer`](file:///C:/Users/user/.gemini/config/skills/seo-reviewer/SKILL.md), [`ai-note-image-reviewer`](file:///C:/Users/user/.gemini/config/skills/ai-note-image-reviewer/SKILL.md), [`pricing-consistency-checker`](file:///C:/Users/user/.gemini/config/skills/pricing-consistency-checker/SKILL.md)
- **SWARM監査**: [`swarm-reviewer`](file:///C:/Users/user/.gemini/config/skills/swarm-reviewer/SKILL.md)

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

## 📅 投稿・公開運用ルール（厳格遵守）

### 1. 投稿の承認必須原則
- ユーザーから明示的に**「投稿してOK」「公開してOK」「本番反映してOK」**という指示・承認があるまで、作成・修正した記事内容をWordPressへ投稿（公開/予約投稿/上書き更新）してはならない。
- それまではローカルのMarkdown原稿（`content/posts/`）やアセット（`assets/images/`）の作成・レビューにとどめること。

### 2. 公開日時の自動計算ルール（「投稿してOK」受領時）
ユーザーから「投稿してOK」の指示があった場合、以下のロジックに従って公開日時（`post_date` / `post_date_gmt` / `post_status`）を自動決定して投稿を行う：

1. **最新（最後）の投稿の公開日（`last_post_date`）を取得する**。
2. **`target_date = last_post_date + 1日` を算出する**。
3. **日付判定**:
   - **`target_date` が「本日（実行日）」より以前の過去日の場合**:
     - 公開日: **本日（実行日）の 朝 08:00:00（JST）**
     - ステータス: `publish`（本日の8時以降であれば即時公開、8時前なら本日8時予約）
   - **`target_date` が「本日（実行日）」以降の未来日の場合**:
     - 公開日: **`target_date` の 朝 08:00:00（JST）**
     - ステータス: `future`（予約投稿）

### 3. カテゴリー投稿数バランス考慮原則（次回提案時の必須義務）
- **累計件数 ＆ 直近ローテーションの事前分析義務**:
  - 次の投稿テーマや連載企画を検討・提案する際は、必ず事前に各カテゴリー（🏪 **街角サバイバル**、🌏 **カルチャーショック**、🔍 **くらべてみました**、🗣️ **ことばのあや**等）の「累計公開・予約本数」および「直近の投稿順（ローテーション状況）」を集計・可視化すること。
### 5. 投稿タイトル命名規則（全カテゴリー名プレフィックス必須ルール）
- **プレフィックスの義務化**:
  - すべての投稿タイトルの先頭には、該当カテゴリーの正式プレフィックス（`くらべてみました：`、`街角サバイバル：`、`ことばのあや：`、`カルチャーショック：`）を全角コロン `：` で付与することを不可侵のルールとする。
  - 「くらべて納得！」や「カルチャーショック！」等の表記揺れは廃止し、WordPress正式カテゴリー名に完全一致させる。
  - 詳細は [`docs/domains/post-title-guidelines.md`](file:///c:/Users/user/git/oscss-wp-nihongo/docs/domains/post-title-guidelines.md) を参照。
- **デプロイ時自動補完ガード**:
  - `scripts/core/repair_all_posts_gutenberg.py` にプレフィックス自動補完ガードを常時有効化し、プレフィックス抜けの記事が本番へ登録されるのを100%防止する。

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

### 毎週定期SEO監査スケジュール (Weekly Scheduled SEO Review)
- **定期実行トリガー**: 毎週月曜日 朝 09:00:00（JST）（cron: `0 9 * * 1`）
- **実行内容**: `scripts/audit/live_seo_reviewer_check.py` および `scripts/audit/audit_site_seo.py` を実行し、全記事・カテゴリーのタイトルタグ、メタディスクリプション、見出し階層、alt属性、JSON-LD構造化データ、トピッククラスターリンク、およびGSC流入キーワードの健全性を包括監査する。

---

## 🎨 サムネイル画像レビュー ＆ 投稿ライフサイクルフック (Mandatory Image Reviewer Hooks)

記事のサムネイル生成時（`post_image_generation`）、Markdown保存時（`post_file_save`）、および投稿・公開前（`pre_post_publish`）には、[`.gemini/skills/image-reviewer/SKILL.md`](file:///c:/Users/user/git/oscss-wp-nihongo/.gemini/skills/image-reviewer/SKILL.md) が自動発動し、以下の品質ゲートを通過することを必須条件とします：

### 0. 【必須義務】4大カテゴリー別サムネイル完全統一規格の事前確認 ＆ 照合義務
- **画像生成およびレビューの前段階で、必ず [`.gemini/skills/image-reviewer/SKILL.md`](file:///c:/Users/user/git/oscss-wp-nihongo/.gemini/skills/image-reviewer/SKILL.md) の「第4章：4大カテゴリー別サムネイル完全統一規格 (Thumbnail Design Systems)」を熟読し、該当カテゴリーのレイアウト・全必須要素・正本マスター画像と完全照合すること**。
- 推測や自己流の構図で画像を生成・レビューすることを固く禁じ、必ず各カテゴリーの統一テンプレート（パネル位置、ピルタグ、吹き出し、RPGコマンド、対比カード、VSロゴ等）を完全に満たしていることを確認する。

1. **主人公「オスカー（クルマ）」の登場必須（公式モデル原型: `assets/images/hero-oscar.png`）**:
   - 正本 `hero-oscar.png` の温かい絵本・コミックエッセイ風タッチ、ふんわり茶髪くせ毛マッシュ、大きめの黒縁丸メガネ、くすみ水色スウェット。
   - **腕と手は必ず「左右2本のみ」**（AI特有の腕3本等の奇形を100%排除）。
   - **表情・ポーズの多様性 ＆ 毎回変更義務（厳格ルール）**:
     - **直近のサムネイルと同じポーズ（同じ立ち姿・同じ武器の構え方）の連続採用を禁止**。
     - 記事のシチュエーション・感情・アクションに直結した多彩なポーズ（盾防御・メニュー凝視・頭抱え・財布探し・果敢な前進・逃げ腰・指差し・腕組み・首傾げ等）を毎回新規に切り替えること。
2. **色合い ＆ 画風の絶対基準（Golden Standard）**:
   - **正本マスター**: [`assets/images/hero-oscar.png`](file:///c:/Users/user/git/oscss-wp-nihongo/assets/images/hero-oscar.png) および各カテゴリーの正本サムネイル（`thumb_street_cafe_order_rpg.jpg`、`thumb-kurabete-zenzen-mattaku.jpg`、`thumb-culture-no-trash-cans-clean-streets.jpg` 等）
   - 温かみのある手描き水彩・コミックエッセイ調、柔らかなブラウンの主線、明るく澄んだパステルカラー。
   - **【厳格禁止】硬質な劇画・パキパキCG調・別人青年の排除**: 正本原型と異なるリアルアニメ調や別人フェイスは一切禁止。
3. **4大カテゴリー別完全統一規格の構成要素（必須照合）**:
    - 🏪 **街角サバイバル【RPGバトルコマンド型】**:
      - 正本: thumb_street_cafe_order_rpg.jpg / thumb_street_onsen_sento_rpg.jpg
      - 上部中央白地カード（薄黄色「🏪 街角サバイバル」ピルタグ＋極太見出し＋サブ見出し）＋ 左側勇者クルマ ＋ 右側笑顔の店員/NPC吹き出し ＋ 下部青色RPGコマンド枠（▶たたかう/どうぐ/にげる）。
      - **【毎回持ち物（装備品）変更義務（厳格ルール）】**: 「剣と盾」の固定を禁止。保険証、不在票、千円札、傘、木桶など各現場固有のアイテムを武器・防具として構えさせる。記事本文でも「🎒 今回のダンジョン装備（持ち物リスト）」を必須定義する（詳細は `docs/domains/street-survival-guidelines.md` 参照）。
    - 🔍 **くらべてみました【中央思案 ＆ 対比型】**:
      - 正本: 	humb-kurabete-zenzen-mattaku.jpg / 	humb-kurabete-chotto-sukoshi.jpg
      - 和風青海波ベージュ背景 ＋ 思案クルマ（メモ帳とペン） ＋ 頭上思考もくもく吹き出し。
      - **2者対比（A vs B型）**: 左側オレンジ角丸カード（極太縦書き＋アイコン）＋ 右側水色角丸カード（極太縦書き＋アイコン）＋ 中央立体「VS」ロゴ。
      - **3者比較（A vs B vs C型・3連ステップメーター）【新設規格】**: 確信度・変化順に並ぶ3連均等カード（オレンジ/ブルー/グリーン）＋ 段階的上昇を示すグラデーション矢印 ＋ 横側に配置された思案クルマ。
    - 🗣️ **ことばのあや【耳ペン解説レクチャー型】**:
      - 正本: 	humb-kotoba-sumimasen-faces.jpg / 	humb-kotoba-tsumaranai-mono-melon.jpg
      - パステルラベンダー（#F0E7F5）背景 ＋ 左側クルマ（耳にペンを挟むトレードマーク、解説笑顔）＋ 右側薄紫カード（「〇〇」の話＋解説）＋ 四隅の丸アイコン（電球・ハート等）。
      - **【遊び心バリエーション】**: テーマに応じた小道具（桐箱入り高級メロン、プレゼント等）をクルマが両手で大切そうに抱えたり誇らしげに掲げるポーズを推奨！
    - 🌏 **カルチャーショック【左上公式カード型】**:
      - 正本: 	humb-culture-no-trash-cans-clean-streets.jpg / 	humb-culture-otohime-toilet-sound.jpg
      - 左上白地カード（ベージュ「カルチャーショック」ピルタグ＋極太見出し＋吹き出し尾）＋ 5頭身クルマの驚愕・発見リアクション ＋ リアルな日本の日常風景背景。
4. **共通フォーマット**:
    - 16:9比率（1200×675）、JPGおよびWebP、ポップで読みやすい日本語タイトル文字配置。
5. **記事内挿入図（オスカー登場）の必須配置原則（今後全記事に最低1枚適用）**:
    - すべての記事（全連載カテゴリー共通）において、本文の最も共感を呼ぶハイライトシーンに、**オスカーが登場するシチュエーション挿入イラスト（16:9比率）を必ず最低1枚配置すること**。
    - **【厳格禁止】挿入画内の英語テキストの完全排除**: 吹き出しや思考アイコンに英語を混在させず、純粋な日本語のみで描写する。
    - **【ガジェット原則】PAD・端末は1台のみ**: 机の上にタブレット（PAD）を描く場合、1台のみに絞り、手前にはノートやペンを自然に配置して画面の重複・乱立を防止する。
6. **【厳格禁止】実在の企業名・商標・ロゴの完全排除ルール (No Real Corporate Names or Logos)**:
    - サムネイルおよび本文挿入画のあらゆる要素（車両、看板、パッケージ、制服、ポスター、名札等）において、**実在する企業名・店名・サービス名（例: 佐川急便、ヤマト運輸、セブンイレブン、イオン等）や実在の企業ロゴ・商標（例: 黒猫マーク、運送会社シンボル等）の描画を固く禁止する**。
    - トラック等の配送車両は**無地または完全架空のシンプルなデザイン**とし、看板やパッケージは**一般名詞（「お弁当」「市役所」「コンビニ」「調剤薬局」「不在連絡票」等）**のみで描写すること。
---

## 📝 記事マークアップ ＆ テキスト強調ルール (No Asterisks Policy)

1. **Markdown記号 `**` の使用禁止**:
   - 記事内の強調には、Markdown記号 `**` を使用せず、必ず HTML タグ（`<strong>テキスト</strong>`）を使用する。
   - 吹き出しブロック（`balloon`）、引用（`quote`）、リスト（`list`）、テーブル（`table`）、通常段落のすべてにおいて、画面に `**` の文字が露出しないよう徹底する。

---

## 👁️ 閲覧数（Views）ゼロスタート原則 (Zero-Start Views Policy)

1. **新規投稿の初期PV数は必ず「0」からカウント**:
   - 新規作成・公開するすべての投稿は、初期閲覧数（`_oscss_post_views`）を **0** からスタートさせる（シードデータやダミーの数値を絶対に付与しない）。
   - 実際のユーザーアクセス（閲覧）によってのみインクリメント（+1）される運用を徹底する。

