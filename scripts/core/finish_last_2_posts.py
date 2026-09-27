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

last_2 = {
    172: """
### 💡 コラム：若者言葉の「全然大丈夫」は文法的に間違いなのか？

街中やSNSで若者たちが頻繁に口にする「全然大丈夫（ぜんぜんだいじょうぶ）」というフレーズ。
本来、副詞「全然」は「全然知らない」「全然美味しくない」のように、**後ろに否定形を伴うのが近代日本語のルール**とされてきました。
そのため、肯定的な「大丈夫」と結びつけるのは誤用だと指摘されることがありました。

しかし、近年の文化庁による「国語に関する世論調査」では、**日本人の6割以上が「全然大丈夫」を自然な表現として受け入れている**ことが判明しています。
さらに歴史を遡ると、明治時代の文豪（夏目漱石や芥川龍之介）も「全然〜だ」と肯定文で使っていた記録が多数残っています。
つまり、「全然大丈夫」は単なる若者の乱れではなく、「100%完全に問題ない！」という強い安心感を相手に届けるための、極めてエネルギーに満ちた現代の生きた日本語なのです。
相手の不安を一瞬で吹き飛ばしたい時、ぜひ笑顔で「全然大丈夫ですよ！」と声をかけてあげてください。
""",
    177: """
### 💡 コラム：世界が賞賛する日本の「落とし物」回収率の奇跡

子供の単独通学を可能にしている圧倒的な治安の良さは、日本の**「遺失物（落とし物）の返却率」**のデータにも明確に現れています。

東京都の警視庁が発表したデータによると、年間で警察に届けられる落とし物の現金の総額は、なんと**約40億円**にものぼります！
そして驚くべきことに、そのうちの**約7割以上（約28億円）が持ち主の手元に無事に戻ってきている**のです。
スマートフォンに至っては、落としたiPhoneやAndroidの**80%以上**が拾い主によって警察や駅の窓口に届けられています。

「誰も見ていなくても、神様や天が見ている」「人のものを盗むとバチが当たる」という幼少期からの道徳教育（お天道様が見ている文化）が、子供たちの通学路の安全を守り、世界中から羨望の眼差しを向けられる「奇跡の治安」を支え続けているのです。
"""
}

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

sftp = ssh.open_sftp()
php_fetch = f"""<?php
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
$ids = [172, 177];
$out = [];
foreach ($ids as $id) {{
    $p = get_post($id);
    $out[$id] = [
        'ID' => $p->ID,
        'title' => $p->post_title,
        'content' => $p->post_content,
        'status' => $p->post_status
    ];
}}
echo base64_encode(json_encode($out));
"""
with sftp.open('fetch_last2.php', 'w') as f:
    f.write(php_fetch)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php fetch_last2.php && rm fetch_last2.php')
l2_data = json.loads(base64.b64decode(stdout.read().decode('utf-8').strip()).decode('utf-8'))

updated_payload = []
for post_id, add_md in last_2.items():
    p = l2_data[str(post_id)]
    orig_content = p['content']
    add_html = md_chunk_to_gutenberg(add_md)

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

    clean_t = re.sub(r'<rt>.*?</rt>', '', p['title'])
    clean_t = re.sub(r'<ruby>(.*?)</ruby>', r'\1', clean_t)
    clean_t = re.sub(r'<[^>]+>', '', clean_t).strip()

    updated_payload.append({
        'ID': post_id,
        'post_title': clean_t,
        'post_content': new_content,
        'post_status': p['status']
    })

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
with sftp.open('sync_last2.php', 'w') as f:
    f.write(php_sync)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php sync_last2.php && rm sync_last2.php')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
print("Last 2 posts complete!")
