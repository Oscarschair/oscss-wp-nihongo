import os
import re
import sys
import json
import base64
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.abspath(os.getcwd()))
from scripts.core.gutenberg_parser import parse_markdown_to_gutenberg_full

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

# Load fetched posts for 11 posts that need WP content base
with open('wp_fetched_posts.json', 'r', encoding='utf-8') as f:
    wp_fetched = json.load(f)

# Helper to convert a markdown chunk to Gutenberg HTML
def md_chunk_to_gutenberg(md_text):
    temp_path = "temp_chunk.md"
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write("---\ntitle: \"temp\"\n---\n" + md_text)
    html = parse_markdown_to_gutenberg_full(temp_path)
    if os.path.exists(temp_path):
        os.remove(temp_path)
    return html

def clean_title(title_raw, slug):
    title = re.sub(r'<rt>.*?</rt>', '', title_raw)
    title = re.sub(r'<ruby>(.*?)</ruby>', r'\1', title)
    title = re.sub(r'<[^>]+>', '', title)
    title = title.strip()

    if 'street-japanese' in slug:
        title = re.sub(r'^(?:ストリート日本語|街角サバイバル)[:：]\s*', '', title)
        title = f"街角サバイバル：{title}"
    elif 'japanese-comparing' in slug:
        title = re.sub(r'^(?:くらべてみました|くらべてみよう)[:：]\s*', '', title)
        title = f"くらべてみました：{title}"
    elif 'kotoba-no-aya' in slug:
        title = re.sub(r'^(?:ことばのあや)[:：]\s*', '', title)
        title = f"ことばのあや：{title}"
    elif 'culture-shock' in slug:
        title = re.sub(r'^(?:カルチャーショック)[:：]\s*', '', title)
        title = f"カルチャーショック：{title}"

    return title

# 11 posts with add-ons to WP base content
addons_for_wp_base = {
    109: """
### 💡 実践サバイバル：飲食店で「温かいお湯（白湯）」をもらう神フレーズ

冷たいお水が苦手な方や、薬を飲みたい時、あるいは中華圏出身で温かいお湯を飲みたい時は、遠慮せずに店員さんに声をかけてみましょう。日本のお店でも親切に対応してくれます。

| シチュエーション | おすすめのフレーズ | 店員の反応・備考 |
| :--- | :--- | :--- |
| **白湯（お湯）が欲しい時** | 「すみません、**白湯（さゆ）**か**温かいお湯**をいただけますか？」 | ポットから熱湯を少し冷まして持ってきてくれます |
| **常温の水が欲しい時** | 「氷なしの、**常温（じょうおん）のお水**はありますか？」 | 「氷抜きですね」と対応してくれます |
| **薬を飲みたい時** | 「薬を飲みたいので、**ぬるま湯**をいただけますか？」 | 最も角が立たず、100%快く対応してもらえる魔法の理由づけ |

#### 近年の「白湯ブーム」：日本のコンビニにも並ぶ温かいペットボトルの謎
実は近年、日本国内でも健康志向や冷え性対策として「白湯（さゆ）」が空前のブームになっています。冬になると、コンビニのホットウォーマー（温かいペットボトル飲料コーナー）に、緑茶やコーヒーと並んで**『アサヒ おいしい水 天然水 白湯』**が定番商品として並ぶようになりました。
「ただのお湯がペットボトルで売れるのか！？」と海外の観光客は二度驚きますが、日本の若者や女性の間では「胃腸を温める」「カフェインが入っていない」として大ヒットしています。真冬に街を歩いていて体が冷え切った時は、ぜひコンビニのホットコーナーで白湯を探してみてください。
""",
    111: """
### 💡 なぜ日本人は「降りる駅の直前」に奇跡的に目覚めるのか？

日本の電車で居眠りしている会社員や学生を見ていると、もう一つ不思議な超能力に気づきます。それは、**「爆睡していたはずなのに、自分の降りる駅に電車が滑り込んだ瞬間にパッと目を開けて何事もなかったかのように降りていく」**という現象です。

これには以下の3つの秘密があると言われています：

1. **駅メロディ（発車メロディ・接近メロディ）の刷り込み**: 日本の各主要駅には固有のメロディがあり、無意識下で耳が自分の駅を認識しています。
2. **電車の加減速とカーブの体感記憶**: 毎日同じ路線に乗っているため、電車の揺れや減速のタイミング、ポイント通過の振動を体が覚えています。
3. **車内アナウンスのトーン**: 独特の落ち着いたトーンで流れる「次は〜、〇〇〜」という自動放送が、脳の覚醒スイッチとして機能しています。

#### もし隣の人に寄りかかってしまったら？電車のマナーとスマートなお詫び
電車が揺れた拍子に、隣の見知らぬ人の肩に頭がコテンと乗っかってしまうのは、日本人でもよくあるハプニングです。そんな時は、目を覚ました瞬間に慌てずにこう対応しましょう。

| シチュエーション | 正しいリアクション・一言 | NGな対応 |
| :--- | :--- | :--- |
| **軽く肩に触れて起きた時** | 小さく頭を下げて「**あっ、すみません！**」 | 何も言わずに知らんぷりして反対側を向く |
| **相手が迷惑そうに身じろぎした時** | 体を起こして「**大変失礼いたしました**」 | 舌打ちしたりスマホを見つめて無視する |
| **自分が寄りかかられた時** | 少し肩を動かして気付かせる（無理に突き飛ばさない） | 激怒したり大声で怒鳴る（トラブルの元） |

車内では7人掛けシートの「両端の座席（ポールや壁がある席）」が最も人気で、奪い合いになるのも日本の通勤電車の名物風景です。
""",
    127: """
### 💡 「ね」「よ」「よね」の3大終助詞マトリクス比較表

終助詞の使い分けで迷った時は、「自分と相手のどちらがその情報を知っているか」を整理すると一発で理解できます。

| 終助詞 | 話者（自分）の知識 | 聞き手（相手）の知識 | ニュアンス・目的 | 例文 |
| :--- | :---: | :---: | :--- | :--- |
| **ね** | 知っている | 知っている（はず） | **共感・同意・親近感** | 「今日、暑い**ね**」（お互い暑さを感じている） |
| **よ** | 知っている | 知らない（はず） | **情報伝達・教示・主張** | 「明日は雨が降る**よ**」（相手が知らない情報を教える） |
| **よね** | 確信がない/確認したい | 知っている（はず） | **確認・再同意・クッション** | 「明日の会議、10時からだ**よね**？」（自分の記憶の最終確認） |

#### ビジネスチャット（SlackやTeams）での「よね」の活用法
現代の日本のビジネス現場では、メールよりもチャットツール（Slack、Teams、LINE WORKSなど）でのやり取りが主流になっています。
チャットでは過剰に硬い敬語を使うと冷たく感じられ、かといってタメ口は失礼になります。そこで大活躍するのが「**敬語＋よね（ですよね）**」のコンビネーションです。

- **催促する時**:
  - ❌ 冷たい例：「企画書の提出期限は本日ですが、まだですか？」
  - ⭕ 柔らかい例：「こちらの企画書、提出期限は本日**ですよね**？進捗はいかがでしょうか？」
- **相手の意見を尊重しつつ確認する時**:
  - ❌ 一方的な例：「この仕様で進めます。」
  - ⭕ 協調的な例：「方向性としては、こちらの仕様で合意いただいた認識**ですよね**？問題なければ着手します！」

このように、「ですよね」を一言添えるだけで、相手へのリスペクトと柔らかい信頼関係を瞬時に演出することができます。
""",
    144: """
### 💡 「いいです」「結構です」「大丈夫です」の曖昧3大フレーズ比較表

日本語学習者を最も悩ませるのが、この「肯定にも否定にも取れる3大フレーズ」です。ネイティブがどのような感覚で使い分けているのか、危険度とともに整理しました。

| フレーズ | 基本の意味 | 誤解されるリスク | 最も安全で誤解のない言い換え |
| :--- | :--- | :---: | :--- |
| **いいです** | ① 許可・OK（YES）<br>② 不要・断り（NO） | ★★★★★<br>（最大級） | ・YESなら：「**ぜひお願いします**」<br>・NOなら：「**いりません / 必要ありません**」 |
| **結構です** | ① 十分・満足（YES）<br>② もう十分だから不要（NO） | ★★★★☆ | ・YESなら：「**それで進めてください**」<br>・NOなら：「**お気持ちだけいただきます**」 |
| **大丈夫です** | ① 問題ない・平気（YES）<br>② 必要ない・構わない（NO） | ★★★★★<br>（頻出） | ・YESなら：「**問題ありません / はい、お願いします**」<br>・NOなら：「**間に合っています / 結構です**」 |

#### コンビニ・スーパーのレジで100%誤解されない黄金ルール
レジで「レジ袋はいかがですか？」「温めますか？」「ポイントカードはお持ちですか？」と次々に聞かれた時、「いいです」と答えると店員さんが一瞬フリーズすることがあります。
誤解をゼロにするための黄金ルールは、**「はい / いいえ」＋「具体的なアクション動詞」**で答えることです。

- 🛍 **レジ袋**:
  - 要る場合：「**はい、1枚お願いします**」
  - 要らない場合：「**いいえ、持参のバッグがあるので大丈夫です（いりません）**」
- 🍱 **お弁当の温め**:
  - 温める場合：「**はい、温めてください**」
  - そのままの場合：「**このままで大丈夫です**」
- 💳 **レシート**:
  - 要る場合：「**レシートお願いします**」
  - 要らない場合：「**レシートは結構です**」

これだけで、一切の気まずい沈黙やトラブルなく、スムーズに買い物を完了することができます。
""",
    150: """
### 💡 ビジネス敬語の落とし穴：「知っていますか？」と「ご存じですか？」

目上の人やクライアント、上司に対して質問する際、「このニュース、知っていますか？」と尋ねるのは実は失礼にあたる場合があります。

| あなたの立場 | 相手への質問フレーズ | 適切さ | 理由と解説 |
| :--- | :--- | :---: | :--- |
| **友人・同僚へ** | 「〇〇のこと、**知ってる**？ / **分かった**？」 | ⭕ 適切 | 親しい間柄では自然な日常会話表現 |
| **目上の人・取引先へ** | ❌「〇〇のこと、**知っていますか**？」 | ⚠️ 要注意 | 「お前はこんなことも知っているのか？」という上から目線のニュアンスを含みやすい |
| **目上の人・取引先へ** | ⭕「〇〇の件、**ご存じでしょうか**？」 | 💮 完璧 | 「知る」の尊敬語である「ご存じ」を使った最も丁寧で洗練された尋ね方 |

#### 「分かりました」の階層別言い換えマスター
上司から指示を受けた時に「分かりました！」と元気に答える新入社員が多いですが、より改まった場面では一段階上の表現を使うと評価が上がります。

1. **同僚・後輩へ**: 「分かった！」「了解！」（カジュアル）
2. **直属の先輩へ**: 「分かりました！」（標準的な丁寧語）
3. **上司・取引先へ**: 「**かしこまりました**」「**承知いたしました**」（格式の高い謙譲表現）
4. **指示内容を復唱して確認する時**: 「〇〇の件ですね、**承知いたしました**。本日中に対応いたします。」
""",
    1: """
### 💡 ビジネス最上級の謝罪表現：「申し訳ございません」と「恐れ入ります」

社会人として日本で働く際、「ごめんなさい」や「すみません」だけではフォーマルな場を乗り切ることはできません。場面に応じた使い分けをマスターしましょう。

| フレーズ | 使用シーン・対象 | ニュアンス・役割 |
| :--- | :--- | :--- |
| **ごめんなさい** | 家族、恋人、親しい友人 | 純粋な個人的謝罪（ビジネスでは原則NG） |
| **すみません** | 同僚、店員、街中の見知らぬ人 | 軽い謝罪・感謝・呼びかけの万能言葉 |
| **失礼いたしました** | 先輩、上司、社内全体 | 自分の動作やマナー違反に対するフォーマルな謝罪 |
| **申し訳ございません** | 上司、取引先、顧客 | 重大なミスや迷惑をかけた際の公式な謝罪 |
| **大変申し訳ございません** | クライアント、全社トラブル | 最大級の謝罪（平身低頭して誠意を示す） |
| **恐れ入ります** | 目上の人、取引先 | 感謝と申し訳なさが混ざったクッション言葉 |

#### 歩道や電車でぶつかりそうになった時の「瞬発力」
街中を歩いていて人と肩がぶつかりそうになったり、電車のドア前で人の前を横切る時は、深く考える前に「**あっ、すみません！**」と小さく頭を下げながら声を発するのが最も安全です。
無言で通り過ぎると「失礼な人だ」とトラブルの原因になりますが、コンマ5秒で「すみません」が出せるようになれば、日本の街角サバイバルは完璧です。
""",
    19: """
### 💡 「ね」の使いすぎに注意？「なれなれしい」と「親近感」の境界線

終助詞「ね」は共感を生み出す魔法の言葉ですが、相手との関係性や立場の上下によっては、思わぬ落とし穴になることがあります。

#### 目上の人に対する「ですね」の罠
上司や取引先との会話で、「そうですね」「いいですね」と相槌を打つのは問題ありません。しかし、**評価や判断を下すような場面で「ね」を使うと上から目線に聞こえる**危険があります。

- ❌ 危険な例（上司の発表に対して）：「部長、素晴らしいプレゼンでした**ね**！」
  - 👉 上司を自分が採点・評価したようなニュアンス（「よくできましたね」と同等）を与えてしまうことがあります。
- ⭕ 洗練された例：「部長、大変勉強になりました。素晴らしいプレゼンをありがとうございました。」

#### クッション言葉としての「そうですね…」の威力
逆に、ビジネスで相手の意見に反対したい時や、難しい質問をされた時、ワンクッション置くために使う「そうですね…」は非常に有効です。
- 「いきなり『違います』と否定するのではなく、**『そうですね…確かにその点もございますが、別の視点として〜』**と受けてから自説を展開する。」
このように、「ね」を相手の感情を包み込む緩衝材として使うことで、どんなに難しい交渉でも角を立てずに前進させることができます。
""",
    30: """
### 💡 留学生必見：日本の奨学金の種類と「勝ち取るための戦略」

海外漢字圏出身者にとって「奨学金＝返さなくていい褒賞金」というイメージが強いため、日本の学生の大半が「借金（貸与型奨学金）」を背負って大学に通っている現実は大きな衝撃です。
では、日本で学ぶ外国人留学生が「返済不要の給付型奨学金」を獲得するにはどうすればよいのでしょうか？

| 奨学金の種類 | 主な提供団体 | 特徴と返済義務 | 獲得の難易度 |
| :--- | :--- | :--- | :---: |
| **文部科学省（国費）奨学金** | 日本国政府（MEXT） | 学費全額免除＋月額11万円〜14万円支給（返済不要） | ★★★★★<br>（最難関） |
| **JASSO（学習奨励費）** | 日本学生支援機構 | 月額48,000円支給（返済不要）成績・出席率重視 | ★★★☆☆<br>（一般的） |
| **民間企業・財団奨学金** | ロータリークラブ、似鳥国際、平和中島等 | 月額5万〜15万円支給（返済不要）面接や小論文あり | ★★★★☆ |
| **大学独自の授業料減免** | 各大学・専門学校 | 学費が30%〜全額免除になる制度 | ★★☆☆☆<br>（狙い目） |

#### 奨学金面接で受かるための3大ポイント
民間財団の面接試験では、単に成績が良いだけでなく、以下のポイントが厳しく見られます：
1. **将来のビジョンと母国・日本への架け橋**: 「将来、日本で学んだ知識を活かして、自分の国と日本の友好関係やビジネスにどう貢献したいか」を明確に語れること。
2. **出席率と日々の態度**: 日本の教育機関は「出席率（90%以上必須）」を極端に重視します。どんなに頭が良くても遅刻や欠席が多いと推薦されません。
3. **日本語でのコミュニケーションへの意欲**: 流暢さだけでなく、一生懸命に自分の言葉で伝えようとする熱意と礼儀正しさが選考委員の心を動かします。
""",
    36: """
### 💡 「おかしい」の多重人格：「笑える」と「怪しい・異常」の見分け方

「おかしい」という言葉には、ポジティブな「ユーモアがあって笑える（funny）」という意味と、ネガティブな「論理が破綻している、怪しい、壊れている（strange / weird / wrong）」という全く異なる2つの顔があります。

| 例文 | 意味 | 英語の対応 | ニュアンス・状況 |
| :--- | :--- | :--- | :--- |
| 「彼の話は**おかしくて**お腹が痛い」 | 笑える | Funny / Hilarious | コメディ、冗談、ユーモア |
| 「この計算、どこか**おかしい**よ」 | 間違っている | Wrong / Incorrect | 数値の不一致、計算ミス |
| 「深夜に知らない人が立っていて**おかしい**」 | 怪しい・不気味 | Strange / Suspicious | 治安への不安、異常事態 |
| 「スマホの画面の動きが**おかしい**」 | 故障している | Malfunctioning | 動作不良、バグ |

#### 関西弁「おもろい」の持つ絶大なリスペクト
関西（大阪・京都・兵庫など）では、「おもしろい」が短縮されて**「おもろい」**となりますが、関西人にとって「あいつ、おもろいやつやな」というのは、**人間に対する最大級の褒め言葉**です。
単にギャグが言えるだけでなく、「人柄に深みがある」「機転が利く」「一緒にいて楽しい」という意味がすべて込められています。
もし関西の人から「おもろいなあ！」と言われたら、最高の賛辞として胸を張りましょう。
""",
    44: """
### 💡 本場の中華料理（ガチ中華）を見分ける看板とキーワード

最近の日本では、池袋や高田馬場、西川口などを中心に、日本人向けにアレンジされていない本場の味を提供する**「ガチ中華（本物の中華料理店）」**が大ブームになっています。
もし日本で「本場の味が恋しい！」と思ったら、以下の特徴をチェックしてみてください。

| 見分けポイント | 日本風の町中華 | 本場のガチ中華 |
| :--- | :--- | :--- |
| **メニューの言語** | 日本語のみ（ひらがな多め） | **中国語（簡体字/繁体字）が大きく書かれている** |
| **定番メニュー** | ラーメン、半チャーハン、餃子、天津飯 | **麻辣燙（マーラータン）、羊肉串（ヤンロウチュアン）、水餃子、米線** |
| **卓上調味料** | 醤油、酢、ラー油、コショウ | **黒酢（鎮江香醋）、自家製麻辣油、花椒油** |
| **店内のBGM・テレビ** | 日本のテレビ番組、J-POP | **中国の流行歌、C-POP、抖音（TikTok）のBGM** |

#### 「町中華で飲ろうぜ」：日本の若者に再評価されるレトロカルチャー
昭和の面影を色濃く残す赤いカウンター、油で少しギトギトしたメニュー表、威勢のいい店主とおかみさん。
近年、日本のテレビ番組やSNS（InstagramやYouTube）を中心に、若い世代の間でこうした古い「町中華」を巡り、昼から瓶ビールと餃子を楽しむレトロ文化が大流行しています。高級中華やファミレスにはない「人情味と圧倒的な安さ、そしてどこか懐かしい味」こそが、町中華が半世紀以上にわたって愛され続ける最大の理由です。
""",
    85: """
### 💡 「よ」の押し付け感に注意！相手を怒らせないためのセーフティガイド

終助詞「よ」は、「相手が知らない情報を教える・伝える」という素晴らしい機能を持っていますが、使い方を誤ると**「上から目線で押し付けがましい」**と受け取られることがあります。

#### 避けるべきNGシチュエーション
1. **相手がすでに知っていることに対して言う**:
   - 相手：「明日は雨だね」
   - ❌ NG：「明日は雨が降る**よ**！」（知ってるから今言ったのに……と相手はイラッとします）
   - ⭕ OK：「本当だね、傘を持っていかないとね」
2. **目上の人に対してアドバイスする時**:
   - ❌ NG：「部長、この資料は修正したほうがいいです**よ**」
   - ⭕ OK：「部長、こちらの資料、修正をご検討いただけますでしょうか」

#### イントネーションによる感情の違い
「よ」は、語尾の音の上がり下がり（ピッチ）で意味が劇的に変わります：
- **ピッチが上がる（⤴）**: 「これ、おいしい**よ**⤴！」（親切なオススメ、喜びの共有）
- **ピッチが強く短く切れる（⤵）**: 「だから言ったでしょ**よ**⤵！」「早くして**よ**⤵！」（不満、非難、苛立ちの表明）

外国人が話す時は、できるだけ語尾を柔らかく、少し高めのトーンで優しく発音すると、親切でフレンドリーな印象を100%相手に届けることができます。
"""
}

# The remaining 11 posts that have local Markdown ready for full Gutenberg conversion
targets_local_md = [
    (158, "content/posts/2026-09-09-culture-shock-carb-on-carb-combos-in-japan-ramen-fried-rice-gyoza-rice-vermicelli.md"),
    (161, "content/posts/2026-09-10-culture-shock-cash-on-delivery-refused-tip-keep-the-change.md"),
    (167, "content/posts/2026-09-10-culture-shock-haircut-price-5000-yen-vs-1000-yen-cut-hong-kong-comparison.md"),
    (164, "content/posts/2026-09-10-japanese-comparing-sayonara-and-matane-differences-in-goodbye-expressions.md"),
    (184, "content/posts/2026-09-11-street-japanese-convenience-store-register-survival-guide.md"),
    (172, "content/posts/2026-09-11-kotoba-no-aya-the-trap-of-daijoubu-yes-or-no-japanese-magic-phrase.md"),
    (187, "content/posts/2026-09-11-street-japanese-hair-salon-survival-shampoo-trap-guide.md"),
    (175, "content/posts/2026-09-12-culture-shock-cars-stop-when-you-raise-your-hand-pedestrian-crosswalk-in-japan.md"),
    (177, "content/posts/2026-09-13-culture-shock-japanese-first-graders-walk-to-school-alone-safety-and-independence.md"),
    (180, "content/posts/2026-09-14-kotoba-no-aya-particles-zo-and-ze-anime-vs-real-life-japanese.md"),
    (182, "content/posts/2026-09-15-japanese-comparing-ageru-kureru-morau-differences-in-giving-and-receiving.md"),
]

posts_payload = []

# Process the 11 WP base posts
for post_id, add_md in addons_for_wp_base.items():
    p_data = wp_fetched[str(post_id)]
    orig_content = p_data['content']
    slug = p_data['name']
    title_raw = p_data['title']
    clean_t = clean_title(title_raw, slug)

    add_html = md_chunk_to_gutenberg(add_md)

    # Insert before vocab box
    # Search for common vocab markers: "今回の語彙", "c-vocab-box"
    vocab_pos = orig_content.find("今回の語彙")
    if vocab_pos == -1:
        vocab_pos = orig_content.find("c-vocab-box")
    
    if vocab_pos != -1:
        # Find the beginning of the block or heading containing vocab
        # Walk backward to find <!-- wp:heading or <h2
        h_pos = orig_content.rfind("<!-- wp:heading", 0, vocab_pos)
        if h_pos == -1:
            h_pos = orig_content.rfind("<h2", 0, vocab_pos)
        if h_pos != -1:
            new_content = orig_content[:h_pos] + add_html + "\n\n" + orig_content[h_pos:]
        else:
            new_content = orig_content[:vocab_pos] + add_html + "\n\n" + orig_content[vocab_pos:]
    else:
        new_content = orig_content + "\n\n" + add_html

    posts_payload.append({
        'ID': post_id,
        'post_title': clean_t,
        'post_name': slug,
        'post_content': new_content,
        'post_excerpt': p_data['excerpt'],
        'post_date': p_data['date'],
        'post_status': p_data['status']
    })

# Process the 11 local MD posts
for post_id, md_path in targets_local_md:
    with open(md_path, 'r', encoding='utf-8') as f:
        raw_md = f.read()

    title_m = re.search(r'title:\s*"([^"]+)"', raw_md)
    desc_m = re.search(r'description:\s*"([^"]+)"', raw_md)
    date_m = re.search(r'date:\s*"([^"]+)"', raw_md)
    slug_m = re.search(r'slug:\s*"([^"]+)"', raw_md)

    slug = slug_m.group(1) if slug_m else ""
    title_raw = title_m.group(1) if title_m else ""
    desc = desc_m.group(1) if desc_m else ""
    date_str = date_m.group(1) if date_m else ""

    clean_t = clean_title(title_raw, slug)

    m_date = re.match(r'(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})', date_str)
    if m_date:
        post_date = f"{m_date.group(1)} {m_date.group(2)}"
    else:
        post_date = ""

    gutenberg_html = parse_markdown_to_gutenberg_full(md_path)

    posts_payload.append({
        'ID': post_id,
        'post_title': clean_t,
        'post_name': slug,
        'post_content': gutenberg_html,
        'post_excerpt': desc,
        'post_date': post_date,
        'post_status': 'publish'
    })

print(f"Prepared {len(posts_payload)} posts for final sync.")
for p in posts_payload:
    print(f"  ID {p['ID']}: [{p['post_status']}] [{p['post_date']}] {p['post_title'][:40]}... (Content len: {len(p['post_content'])} chars)")

# Serialize to JSON and encode in base64
payload_json = json.dumps(posts_payload, ensure_ascii=False)
payload_b64 = base64.b64encode(payload_json.encode('utf-8')).decode('ascii')

# Connect to SSH
print("\nConnecting to SSH server...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    hostname=env['SSH_HOST'],
    port=int(env['SSH_PORT']),
    username=env['SSH_USER'],
    password=env['SSH_PASS'],
    look_for_keys=False,
    allow_agent=False
)
sftp = ssh.open_sftp()
print("Connected!")

# Transfer batch sync script
php_sync_script = f"""<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$b64 = '{payload_b64}';
$data = json_decode(base64_decode($b64), true);

if (!$data) {{
    echo "ERROR: Failed to decode json payload\\n";
    exit(1);
}}

foreach ($data as $item) {{
    $post_arr = array(
        'ID'           => $item['ID'],
        'post_title'   => $item['post_title'],
        'post_content' => $item['post_content'],
        'post_excerpt' => $item['post_excerpt'],
        'post_status'  => $item['post_status']
    );

    if (!empty($item['post_date'])) {{
        $post_arr['post_date'] = $item['post_date'];
        $timestamp = strtotime($item['post_date']) - (9 * 3600);
        $post_arr['post_date_gmt'] = gmdate('Y-m-d H:i:s', $timestamp);
    }}

    $res = wp_update_post($post_arr, true);
    if (is_wp_error($res)) {{
        echo "[ERROR] Post " . $item['ID'] . ": " . $res->get_error_message() . "\\n";
    }} else {{
        $p = get_post($item['ID']);
        $read_time = function_exists('oscss_get_reading_time') ? oscss_get_reading_time($p) : 0;
        echo "[UPDATED] Post " . $item['ID'] . " | Date: " . $p->post_date . " | Status: " . $p->post_status . " | Title: " . mb_substr($p->post_title, 0, 30) . "... | Reading time: 約" . $read_time . "分\\n";
    }}
}}

// Purge LiteSpeed Cache
if (has_action('litespeed_purge_all')) {{
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache successfully purged!\\n";
}}
"""

with sftp.open('sync_batch_22_posts.php', 'w') as f:
    f.write(php_sync_script)

print("\nExecuting sync_batch_22_posts.php on remote server...")
stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php sync_batch_22_posts.php && rm sync_batch_22_posts.php', timeout=120)
print(stdout.read().decode('utf-8', errors='replace'))
err = stderr.read().decode('utf-8', errors='replace')
if err:
    print("Stderr:", err)

sftp.close()
ssh.close()
print("All 22 posts synced successfully!")
