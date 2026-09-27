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

def md_chunk_to_gutenberg(md_text):
    temp_path = "temp_chunk.md"
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write("---\ntitle: \"temp\"\n---\n" + md_text)
    html = parse_markdown_to_gutenberg_full(temp_path)
    if os.path.exists(temp_path):
        os.remove(temp_path)
    return html

# 8 posts final finish (adds 750 - 1,000 pure text characters each)
finish_packs = {
    158: """
### 💡 理解度チェッククイズ：日本の炭水化物文化マスター

今回の学習内容を振り返る3つの確認テストです。正しい答えを選んでみてください。

- **第1問：関西の定食屋で「お好み焼き定食」を頼むと、お好み焼きと一緒に何が出てくる？**
  - ① パンと牛乳
  - ② 白ご飯とお味噌汁
  - ③ フライドポテトとコーラ
  - 👉 **正解は②！** 濃厚なソースとマヨネーズはお米の最高のおかずとして愛されています。

- **第2問：中国や香港の本場の餃子と、日本の焼き餃子の決定的な違いは何？**
  - ① 日本の餃子は皮が極限まで薄く、白米のおかずとして進化した
  - ② 日本の餃子は甘いデザートである
  - ③ 日本の餃子は茹でて食べるのが基本である
  - 👉 **正解は①！** 本場では分厚い皮の主食ですが、日本ではパリッとした薄皮のおかずに生まれ変わりました。

- **第3問：炭水化物を美味しく楽しんだ後、健康を保つための賢い知恵は？**
  - ① 翌日まで絶食する
  - ② 野菜や発酵食品（味噌汁）をバランスよく摂り、よく歩く
  - ③ すぐに横になって眠る
  - 👉 **正解は②！** バランスと日常の運動が日本人の健康寿命の秘密です。
""",
    167: """
### 💡 理解度チェッククイズ：日本の理美容室サバイバルマスター

1000円カットとサロンを使いこなすための確認テストです。

- **第1問：1000円カット（QBハウス等）でカットが終わった後、頭に残った細かい毛はどうやって処理される？**
  - ① シャンプー台で丁寧に泡立てて洗う
  - ② 専用のエアクリーナー（掃除機のような吸引機）で一瞬で吸い取る
  - ③ タオルで激しく叩いて払う
  - 👉 **正解は②！** 水を使わないこの超効率システムこそが、10分カットを実現する最大の技術です。

- **第2問：一般美容院の予約時、「静かに過ごしたい」時に一番効果的な方法は？**
  - ① 耳栓をして入店する
  - ② ネット予約（Hot Pepper Beauty等）の要望欄で「なるべく静かに過ごしたい」を選択する
  - ③ ずっと寝たふりをする
  - 👉 **正解は②！** 事前に設定しておけば、美容師が必要最小限の確認だけで心地よい空間を作ってくれます。

- **第3問：美容室で仕上がりのイメージを最も正確に伝える方法は？**
  - ① 正面・サイド・後ろ姿の「イメージ写真」をスマホで見せる
  - ② 「いい感じにお願いします」とだけ言う
  - ③ 目を閉じて念じる
  - 👉 **正解は①！** 視覚的な写真は、どんな言葉による説明よりも100倍確実に伝わります。
""",
    164: """
### 💡 理解度チェッククイズ：別れ際の挨拶マスター

状況に応じた完璧な別れ際の言葉を選んでみましょう。

- **第1問：職場で定時になり、まだ残業している先輩や同僚より先に退勤する時の正しい挨拶は？**
  - ① 「さようなら！」
  - ② 「ご苦労様でした！」
  - ③ 「お疲れ様でした、お先に失礼します！」
  - 👉 **正解は③！** 周囲への労いと配慮を込めた最も美しい退勤の挨拶です。

- **第2問：現代の日本人が親しい友人に「さようなら」と言わない最大の理由は？**
  - ① 「二度と会わない」「永遠の別れ」のような重い響きがあるから
  - ② 発音が難しすぎるから
  - ③ 法律で禁止されているから
  - 👉 **正解は①！** 日常の友達には「またね！」「じゃあね！」と再会を前提にした言葉を使います。

- **第3問：取引先とのオンライン会議（Zoom等）を退出する際のマナーは？**
  - ① 何も言わずにいきなり「退出」ボタンを押す
  - ② 「本日はありがとうございました。失礼いたします」と挨拶し、一礼してから退出する
  - ③ 大きく手を振ってバイバイする
  - 👉 **正解は②！** オンラインであっても画面越しの礼儀作法が相手への信頼を深めます。
""",
    172: """
### 💡 理解度チェッククイズ：「大丈夫」の真意解読マスター

日本人が発する「大丈夫」の意味を正確に見抜くテストです。

- **第1問：コンビニのレジで店員に「お箸はおつけしますか？」と聞かれ、「あ、大丈夫です」と答えた時の意味は？**
  - ① 「はい、お箸をたくさんください」
  - ② 「いいえ、お箸はいりません」
  - ③ 「お箸の強度が心配です」
  - 👉 **正解は②！** 手を軽く振ったり添えたりする「大丈夫」は99%が「辞退（不要）」の合図です。

- **第2問：職場で上司に進捗を聞かれた時、最も信頼を落とす危険な回答は？**
  - ① 「現在70%完了しており、明日15時に初稿を提出できます」
  - ② 「はい、大丈夫です！（実はまだ3割しかできていない）」
  - ③ 「少し遅れているため、優先順位をご相談させてください」
  - 👉 **正解は②！** 主観的な「なんとかなる」の大丈夫は、納期直前の大炎上を招きます。

- **第3問：自分が相手に何かを頼む時、「大丈夫」の代わりに使うべき明確な言葉は？**
  - ① 「はい、ぜひお願いします！」
  - ② 「どっちでもいいです」
  - ③ 「お任せします」
  - 👉 **正解は①！** 肯定の時は明確な意思表示をすることで、相手に安心感を与えられます。
""",
    175: """
### 💡 理解度チェッククイズ：日本の横断歩道サバイバルマスター

歩行者優先ルールを100%安全に活用するための確認テストです。

- **第1問：信号機のない横断歩道を渡りたい時、車に気づいてもらう最も効果的な方法は？**
  - ① 道路に飛び出す
  - ② 右手をピッと高く挙げて、渡る意思を示す
  - ③ 立ち止まってスマートフォンを見る
  - 👉 **正解は②！** 手を挙げることで、遠くを走るドライバーの視界に確実に認識されます。

- **第2問：車が横断歩道の手前で一時停止してくれた時、渡りながらすべきマナーは？**
  - ① ドライバーに向かってペコッと軽く頭を下げる（会釈する）
  - ② 無視してゆっくり歩く
  - ③ 車を睨みつける
  - 👉 **正解は①！** 感謝の会釈を交わすことで、お互いに温かい気持ちで安全運転が継続されます。

- **第3問：手前の車が止まってくれた時に、絶対に油断してはいけない危険は何？**
  - ① 手前の車が急発進すること
  - ② 対向車線やすり抜けのバイクが死角から突っ込んでくること（サンキュー事故）
  - ③ カラスが飛んでくること
  - 👉 **正解は②！** 親切に止まってもらえた時こそ、奥の車線の安全確認を怠らないのが鉄則です。
""",
    177: """
### 💡 理解度チェッククイズ：日本の小学生登校と防犯マスター

子供たちの安全を見守る日本の社会システムについての確認テストです。

- **第1問：日本の小学生が通学時に背負う四角いカバン「ランドセル」の隠された機能は？**
  - ① 万が一川に落ちた時に浮き輪代わりになり、転んだ時の後頭部クッションになる
  - ② GPSで自動で目的地まで飛んでいく
  - ③ 防弾チョッキのように銃弾を跳ね返す
  - 👉 **正解は①！** 6年間の耐久性だけでなく、命を守る安全設計が随所に施されています。

- **第2問：毎朝、通学路の交差点で黄色い旗を持って子供たちを誘導している人々は誰？**
  - ① 警察の特殊部隊
  - ② 地域のボランティアやPTA（緑のおじさん・おばさん）
  - ③ 小学校の校長先生
  - 👉 **正解は②！** 地域住民が無償で子供たちの命を守る温かいコミュニティの絆です。

- **第3問：小学校周辺の道路に緑色でペイントされた「ゾーン30」の意味は？**
  - ① 30人以上で歩かなければいけないエリア
  - ② 車の最高速度が時速30キロに厳しく制限された通学安全エリア
  - ③ 30分間駐車が無料のエリア
  - 👉 **正解は②！** 車のスピードを物理的に抑制し、歩行者の安全を最優先にする設計です。
""",
    180: """
### 💡 理解度チェッククイズ：アニメ日本語vs現実日本語マスター

終助詞「ぞ」「ぜ」のTPOをマスターするための確認テストです。

- **第1問：現実の日本の大人の男性が「行くぞ！」を使う最も自然なシチュエーションは？**
  - ① 初対面の取引先との商談
  - ② 自分自身を奮い立たせる独り言や、スポーツの試合前の気合入れ
  - ③ レストランの店員への注文
  - 👉 **正解は②！** 人に対して使うと威圧的ですが、自分への号令なら非常に自然です。

- **第2問：アニメの主人公が「〜だぜ！」を連発する言語学的な理由は？**
  - ① 現実の日本人が全員そう話しているから
  - ② そのキャラクターの強さや熱血さを一瞬で表現する「役割語」だから
  - ③ 文法的にそれが一番正しいから
  - 👉 **正解は②！** フィクションを分かりやすくするための記号的表現です。

- **第3問：現実の日常会話で友達と親しく話す時、最も自然で好感度の高い語尾は？**
  - ① 「〜でござる」
  - ② 「〜だよ」「〜ね」「〜じゃん」
  - ③ 「〜であるぞよ」
  - 👉 **正解は②！** 柔らかく共感を生む語尾こそが、現代日本語のスタンダードです。
""",
    182: """
### 💡 理解度チェッククイズ：授受表現（あげる・くれる・もらう）マスター

矢印の向きを100%間違えないための確認テストです。

- **第1問：同僚の田中さんが、自分（私）に美味しいお菓子を持ってきてくれた時の正しい日本語は？**
  - ① 「田中さんが私にお菓子をあげました」
  - ② 「田中さんが私にお菓子をくれました」
  - ③ 「私が田中さんにお菓子をもらわせました」
  - 👉 **正解は②！** 相手から自分（内側）に向かう矢印なので「くれる」が100%正解です。

- **第2問：先生や上司など、目上の人から親切にアドバイスをいただいた時の最も丁寧な表現は？**
  - ① 「先生からアドバイスをもらいました」
  - ② 「先生がアドバイスをくれました」
  - ③ 「先生にアドバイスをいただきました」
  - 👉 **正解は③！** 「もらう」の謙譲語である「いただく」を使うことで、深い敬意が伝わります。

- **第3問：ビジネスメールで相手に確認をお願いする時の最もプロフェッショナルな表現は？**
  - ① 「確認してください」
  - ② 「ご確認いただけますと幸いでございます」
  - ③ 「確認をあげます」
  - 👉 **正解は②！** 相手の自主的な親切を引き出す「〜ていただく」は最強のビジネス敬語です。
"""
}

# Fetch current posts from WordPress for these 8 IDs
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

sftp = ssh.open_sftp()
php_fetch = f"""<?php
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
$ids = json_decode('{json.dumps(list(finish_packs.keys()))}', true);
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
with sftp.open('fetch_f8.php', 'w') as f:
    f.write(php_fetch)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php fetch_f8.php && rm fetch_f8.php')
f8_data = json.loads(base64.b64decode(stdout.read().decode('utf-8').strip()).decode('utf-8'))

updated_payload = []
for post_id, add_md in finish_packs.items():
    p = f8_data[str(post_id)]
    orig_content = p['content']
    add_html = md_chunk_to_gutenberg(add_md)

    # Insert before vocab block or heading
    vocab_pos = orig_content.find("今回の語彙")
    if vocab_pos == -1:
        vocab_pos = orig_content.find("c-vocab-box")
    
    if vocab_pos != -1:
        h_pos = orig_content.rfind("<!-- wp:heading", 0, vocab_pos)
        if h_pos == -1:
            h_pos = orig_content.rfind("<h2", 0, vocab_pos)
        if h_pos != -1:
            new_content = orig_content[:h_pos] + add_html + "\n\n" + orig_content[h_pos:]
        else:
            new_content = orig_content[:vocab_pos] + add_html + "\n\n" + orig_content[vocab_pos:]
    else:
        new_content = orig_content + "\n\n" + add_html

    # Clean title
    clean_t = re.sub(r'<rt>.*?</rt>', '', p['title'])
    clean_t = re.sub(r'<ruby>(.*?)</ruby>', r'\1', clean_t)
    clean_t = re.sub(r'<[^>]+>', '', clean_t).strip()

    updated_payload.append({
        'ID': post_id,
        'post_title': clean_t,
        'post_content': new_content,
        'post_status': p['status']
    })

# Sync to WP
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
    echo "ID " . $item['ID'] . " | Final reading time: 約" . $time . "分\\n";
}}
if (has_action('litespeed_purge_all')) {{
    do_action('litespeed_purge_all');
}}
"""
with sftp.open('sync_f8.php', 'w') as f:
    f.write(php_sync)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php sync_f8.php && rm sync_f8.php')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
print("Final 8 posts finish completed!")
