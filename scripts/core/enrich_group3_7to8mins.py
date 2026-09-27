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

# Content additions for Group 3 (ID 175, 177, 180, 182)
group3_addons = {
    175: """
## 信号のない横断歩道で「車が止まる」驚異のメカニズム

海外の多くの都市では、「横断歩道」は道路に白いペンキが塗ってあるだけの場所にすぎず、歩行者が立っていても車は猛スピードで走り去っていきます。
しかし、日本では道路交通法第38条により、**「横断歩道に歩行者がいる場合、車両は直前で一時停止しなければならない」**と法律で厳格に定められています。

### なぜ日本のドライバーは歩行者を優先するのか？
かつては日本でも横断歩道での一時停止率は高くありませんでした。しかし、JAF（日本自動車連盟）による全国調査の公表や、警察による徹底した取り締まり（反則金9,000円、違反点数2点）が進んだことで、ドライバーの意識は劇的に変化しました。

| 国・地域 | 横断歩道での車の挙動 | 歩行者のサバイバル意識 |
| :--- | :--- | :--- |
| **香港・アジア大都市** | 車が優先。クラクションを鳴らして突っ込んでくる | 車の切れ目を狙って全力ダッシュ |
| **欧米主要都市** | 歩行者が足を一歩踏み出すと車が止まる | アイコンタクトを重視 |
| **日本の横断歩道** | **手を挙げて待つと、高確率でスーッと停止** | 止まってくれたドライバーにペコッと会釈して渡る |

### 💡 歩行者が知っておくべき「安全横断3つの神ルール」
1. **右手をピッと高く挙げる**: ドライバーから見えやすいように、しっかりと「渡る意思」を示します。
2. **車が完全に止まるまで足を出さない**: 止まる気配のない車も一定数いるため、車輪が止まるのを必ず目視で確認します。
3. **渡りながら軽く頭を下げる（ペコッ）**: 止まってくれた運転手さんに向けて軽く会釈（感謝のサイン）をすると、お互いにとても気持ちの良い空気が生まれます。

#### トラブル事例：「対向車の死角」に潜む危険（サンキュー事故）
手前の車が親切に止まってくれても、その奥の車線（対向車線やすり抜けのバイク）が歩行者に気づかずに突っ込んでくることがあります。
親切に止まってもらえた時こそ、焦らずに左右をしっかり確認しながら渡るのが、日本での賢い歩行者サバイバル術です。
""",
    177: """
## 小学生が1人で電車に乗って通学する日本の驚異的な治安

アメリカやイギリスなどの欧米諸国では、12歳未満の子供を1人で留守番させたり外出させると、親が**「ネグレクト（育児放棄）」**として警察に通報・逮捕される法律があります。
そのため、日本の小学校1年生（6〜7歳）が大きなランドセルを背負い、たった1人で電車やバスを乗り継いで通学している姿を見た外国人は、文字通り腰を抜かすほど衝撃を受けます。

### なぜ日本では子供の単独通学が可能なのか？
日本が世界一安全な通学環境を実現できているのには、社会全体で張り巡らされた「3重の防犯セーフティネット」が存在するからです。

| セーフティネット | 仕組みと役割 |
| :--- | :--- |
| **地域ボランティア（緑のおじさん・おばさん）** | 毎朝、黄色い旗を持った地域の高齢者やPTAが交差点に立ち、子供たちを安全に誘導。 |
| **集団登校システム** | 近所の子供たちがグループを作り、高学年のリーダーを先頭に一列になって歩く。 |
| **子供110番の家・防犯ブザー** | 商店や民家が「駆け込み寺」として登録され、ランドセルには高音の防犯ブザーを常備。 |

### 💡 ランドセルに隠された日本のハイテクと伝統
小学生が背負っている四角いカバン「ランドセル」は、単なる通学カバンではありません。
- **6年間壊れない超高耐久性**: 職人の手作りで、雨風に強く6年間毎日の使用に耐える。
- **後ろに転んだ時のエアバッグ**: 後頭部を地面に強打しないよう、クッションの役割を果たす設計。
- **水に浮く浮力**: 万が一川や用水路に落ちた場合、ランドセルが浮き輪代わりになる。

社会全体が「街の子供はみんなで見守る」という共同体意識を持っているからこそ、日本の子供たちは幼い頃から自立心と公共マナーを自然に身につけていくことができるのです。
""",
    180: """
## アニメの主人公は使うのに、なぜ現実の日本人は「ぞ」「ぜ」を使わないのか？

『ドラゴンボール』の孫悟空は「オラ、ワクワクすっ**ぞ**！」と言い、『ONE PIECE』のルフィは「海賊王に俺はなる**ぞ**！」と叫びます。
日本語学習者がアニメを見て日本語を覚えると、「日本語の男言葉といえば『〜だぞ』『〜だぜ』だ！」と思い込んで、来日直後に同僚や友達に対して連発してしまい、爆笑されるというお決まりのトラップが存在します。

### 「ぞ」「ぜ」が日常会話から消えた理由
現実の現代日本において、大人の男性が日常会話で「行くぞ！」「そうだぜ！」を使う機会は極めて限定的です。

| 終助詞 | アニメ・漫画の世界 | 現実の日常会話のリアル |
| :--- | :--- | :--- |
| **ぞ** | 主人公の強い決意、命令、警告 | 自分自身への独り言（「よし、やるぞ！」）以外で人に言うと**威圧的・高圧的**に聞こえる |
| **ぜ** | クールでかっこいい男性の語尾 | 冗談やふざけて話す時以外で使うと**「カッコつけすぎ」「時代劇っぽい」**と笑われる |

### 💡 現代の日本人男性が実際に使っている自然な語尾
では、現実の日本人男性はどのように語尾を処理しているのでしょうか？

1. **「〜だよ」「〜ね」**: 最も一般的で自然。柔らかく親しみやすい印象を与える。
   - ⭕「明日、映画行こう**よ**」「これ、美味しい**ね**」
2. **「〜じゃん」「〜っしょ」**: カジュアルなタメ口表現。
   - ⭕「それ、いい**じゃん**！」「間に合う**っしょ**」
3. **「〜だろ」「〜だな」**: 男らしさを少し残した落ち着いた語尾。
   - ⭕「これでいい**だろ**」「今日は疲れた**な**」

アニメの日本語は「キャラクターの性格を一瞬で強調するための記号（キャラ語）」として誇張されています。現実の会話では、柔らかく共感を生む終助詞を選ぶのが、誰からも愛されるコミュニケーションの秘訣です。
""",
    182: """
## 「あげる」「くれる」「もらう」の矢印を完全マスターする物理法則

日本語の授受動詞（もののやり取り）は、英語の「give」や中国語の「給」のように単なる動作を表すのではなく、**「話し手との心理的な距離（ウチとソト）」**を反映する精密なシステムです。

### 迷宮から脱出する「矢印の向き」の絶対ルール
この3つの動詞は、「矢印が自分に向かっているか、相手に向かっているか」だけで100%区別できます。

```
【あげる】（自分 → 相手）
自分から外側の相手へ向かってモノを差し出す。
例：「私は田中さんにプレゼントをあげました」

【くれる】（相手 → 自分）
外側の相手から自分（または自分の家族・仲間）の内側へモノが入ってくる。
例：「田中さんが私にプレゼントをくれました」

【もらう】（自分 ← 相手）
自分が主体となり、外側の相手からモノを受け取る。
例：「私は田中さんからプレゼントをもらいました」
```

### 💡 外国人が絶対にやってしまうNGパターン
最も多い間違いが、相手から自分へのプレゼントに対して「あげる」を使ってしまうことです。
- ❌ **大間違い**: 「先生が私に本を**あげました**」
  - 👉 これを言うと、「先生を自分より下の存在として扱っている」ように聞こえ、非常に不自然です！
- ⭕ **正解**: 「先生が私に本を**くださいました**（くれました）」
- ⭕ **正解**: 「私は先生から本を**いただきました**（もらいました）」

#### 敬語への発展形マトリクス
ビジネスや目上の人との会話では、以下のように敬語へとスライドします：
- **あげる** → **差し上げる（さしあげる）**
- **くれる** → **くださる**
- **もらう** → **いただく**

「親切にしてもらった恩恵」に対して感謝の矢印を正しく向けること。これこそが、日本語の人間関係を円滑にする最も美しいマナーなのです。
"""
}

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()
php_fetch = f"""<?php
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
$ids = [175, 177, 180, 182];
$out = [];
foreach ($ids as $id) {{
    $p = get_post($id);
    $out[$id] = [
        'ID' => $p->ID,
        'title' => $p->post_title,
        'content' => $p->post_content,
        'date' => $p->post_date,
        'status' => $p->post_status,
        'name' => $p->post_name,
        'excerpt' => $p->post_excerpt
    ];
}}
echo base64_encode(json_encode($out));
"""
with sftp.open('fetch_g3.php', 'w') as f:
    f.write(php_fetch)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php fetch_g3.php && rm fetch_g3.php')
g3_data = json.loads(base64.b64decode(stdout.read().decode('utf-8').strip()).decode('utf-8'))

# Merge content and update
updated_payload = []
for post_id, add_md in group3_addons.items():
    p = g3_data[str(post_id)]
    add_html = parse_markdown_to_gutenberg_full(f"content/posts/{p['date'][:10]}-{p['name']}.md")
    
    # We create a rich combined Gutenberg content:
    # Read the local markdown and combine with add_md
    local_md_path = f"content/posts/{p['date'][:10]}-{p['name']}.md"
    with open(local_md_path, 'r', encoding='utf-8') as f:
        local_md = f.read()
    
    # Append the addon before vocab
    if "## 🎯 今回の語彙" in local_md:
        enriched_md = local_md.replace("## 🎯 今回の語彙", add_md + "\n\n## 🎯 今回の語彙")
    else:
        enriched_md = local_md + "\n\n" + add_md
    
    with open(local_md_path, 'w', encoding='utf-8') as f:
        f.write(enriched_md)
    
    # Convert enriched markdown to full Gutenberg HTML
    full_gutenberg = parse_markdown_to_gutenberg_full(local_md_path)
    
    # Clean title
    clean_t = re.sub(r'<rt>.*?</rt>', '', p['title'])
    clean_t = re.sub(r'<ruby>(.*?)</ruby>', r'\1', clean_t)
    clean_t = re.sub(r'<[^>]+>', '', clean_t).strip()
    
    updated_payload.append({
        'ID': post_id,
        'post_title': clean_t,
        'post_content': full_gutenberg,
        'post_name': p['name'],
        'post_excerpt': p['excerpt'],
        'post_date': p['date'],
        'post_status': p['status']
    })

# Sync to WordPress
sftp = ssh.open_sftp()
payload_b64 = base64.b64encode(json.dumps(updated_payload, ensure_ascii=False).encode('utf-8')).decode('ascii')
php_sync = f"""<?php
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
$data = json_decode(base64_decode('{payload_b64}'), true);
foreach ($data as $item) {{
    $res = wp_update_post([
        'ID' => $item['ID'],
        'post_title' => $item['post_title'],
        'post_content' => $item['post_content'],
        'post_status' => $item['post_status']
    ], true);
    $p = get_post($item['ID']);
    $time = oscss_get_reading_time($p);
    echo "ID " . $item['ID'] . " | Updated reading time: 約" . $time . "分\\n";
}}
if (has_action('litespeed_purge_all')) {{
    do_action('litespeed_purge_all');
}}
"""
with sftp.open('sync_g3.php', 'w') as f:
    f.write(php_sync)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php sync_g3.php && rm sync_g3.php')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
print("Group 3 sync complete!")
