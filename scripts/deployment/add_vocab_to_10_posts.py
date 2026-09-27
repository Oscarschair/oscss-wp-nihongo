import os
import sys
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

vocab_definitions = {
    1: [
        {"word": "謝罪（しゃざい）", "jlpt": "N2", "meaning": "apology", "example": "心からの謝罪の気持ちを込めて「ごめんなさい」と言う。"},
        {"word": "恐縮（きょうしゅく）", "jlpt": "N1", "meaning": "feeling obliged, being grateful/sorry", "example": "相手に気を遣わせてしまい大変恐縮する。"},
        {"word": "反省（はんせい）", "jlpt": "N3", "meaning": "reflection, remorse", "example": "失敗を素直に認めて深く反省する。"}
    ],
    19: [
        {"word": "共感（きょうかん）", "jlpt": "N2", "meaning": "sympathy, empathy", "example": "相手の意見に「そうだね」と共感を示す。"},
        {"word": "同調（どうちょう）", "jlpt": "N1", "meaning": "conformity, agreement", "example": "場の空気に合わせて同調の終助詞を使う。"},
        {"word": "納得（なっとく）", "jlpt": "N3", "meaning": "consent, assent, understanding", "example": "説明を聞いて心から納得する。"}
    ],
    30: [
        {"word": "奨学金（しょうがくきん）", "jlpt": "N3", "meaning": "scholarship, student loan", "example": "日本の奨学金には返済義務のある「貸与型」が多い。"},
        {"word": "返済（へんさい）", "jlpt": "N2", "meaning": "repayment, refund", "example": "卒業後に毎月少しずつ奨学金を返済する。"},
        {"word": "借金（しゃっきん）", "jlpt": "N2", "meaning": "debt, loan", "example": "実質的に借金と同じ仕組みであることに驚く。"}
    ],
    36: [
        {"word": "興味（きょうみ）", "jlpt": "N4", "meaning": "interest (in something)", "example": "日本の文化に対して深い興味を持つ。"},
        {"word": "滑稽（こっけい）", "jlpt": "N1", "meaning": "funny, comical, ridiculous", "example": "どこか滑稽で思わず笑ってしまう様子。"},
        {"word": "不思議（ふしぎ）", "jlpt": "N3", "meaning": "wonder, miracle, strange", "example": "理由が分からずとても不思議に感じる。"}
    ],
    85: [
        {"word": "伝達（でんたつ）", "jlpt": "N2", "meaning": "transmission, delivery, communication", "example": "相手が知らない新しい情報を正確に伝達する。"},
        {"word": "指摘（してき）", "jlpt": "N1", "meaning": "pointing out, identification", "example": "間違いを優しく指摘するときに終助詞を使う。"},
        {"word": "親切（しんせつ）", "jlpt": "N4", "meaning": "kindness, gentleness", "example": "親切心からアドバイスを伝える。"}
    ],
    109: [
        {"word": "氷水（こおりみず）", "jlpt": "N3", "meaning": "ice water", "example": "真冬のレストランでも氷水が出されて驚く。"},
        {"word": "習慣（しゅうかん）", "jlpt": "N4", "meaning": "custom, habit", "example": "国によっておもてなしの習慣は大きく異なる。"},
        {"word": "白湯（さゆ）", "jlpt": "N2", "meaning": "plain boiled hot water", "example": "中華圏では体を温めるために白湯を好む。"}
    ],
    111: [
        {"word": "居眠り（いねむり）", "jlpt": "N2", "meaning": "nodding off, dozing", "example": "電車の中で多くの乗客が気持ちよさそうに居眠りしている。"},
        {"word": "治安（ちあん）", "jlpt": "N2", "meaning": "public order, safety", "example": "日本の治安の良さは世界でもトップクラスだ。"},
        {"word": "無防備（むぼうび）", "jlpt": "N1", "meaning": "defenseless, unprotected", "example": "貴重品を持ったまま無防備に眠れる環境に感動する。"}
    ],
    127: [
        {"word": "確認（かくにん）", "jlpt": "N3", "meaning": "confirmation, verification", "example": "相手の記憶を優しく確認するために「よね」を添える。"},
        {"word": "配慮（はいりょ）", "jlpt": "N1", "meaning": "consideration, concern", "example": "角を立てずに伝えるための細やかな配慮。"},
        {"word": "遠慮（えんりょ）", "jlpt": "N3", "meaning": "reserve, hesitation, restraint", "example": "遠慮がちな日本人のコミュニケーション術。"}
    ],
    144: [
        {"word": "辞退（じたい）", "jlpt": "N1", "meaning": "refusal, declining, bowing out", "example": "「結構です」の意味で丁寧に辞退する。"},
        {"word": "承諾（しょうだく）", "jlpt": "N1", "meaning": "consent, acceptance, agreement", "example": "提案を快く承諾するときにも使われる。"},
        {"word": "曖昧（あいまい）", "jlpt": "N2", "meaning": "vague, ambiguous", "example": "文脈によってYESにもNOにもなる曖昧な表現。"}
    ],
    150: [
        {"word": "理解（りかい）", "jlpt": "N3", "meaning": "understanding, comprehension", "example": "内容の意味や道筋を深く理解する「わかる」。"},
        {"word": "知識（ちしき）", "jlpt": "N3", "meaning": "knowledge, information", "example": "情報として記憶に持っている「知っている」。"},
        {"word": "把握（はあく）", "jlpt": "N1", "meaning": "grasp, understanding, catch", "example": "現状の課題を正確に把握して対応する。"}
    ]
}

def generate_box_html(items):
    cards_html = []
    for it in items:
        badge_cls = f"c-badge--jlpt-{it['jlpt'].lower()}"
        card = f"""    <div class="c-vocab-card">
      <div class="c-vocab-card__header">
        <span class="c-vocab-card__word">{it['word']}</span>
        <span class="c-badge c-badge--jlpt {badge_cls}">JLPT {it['jlpt']}</span>
      </div>
      <p class="c-vocab-card__meaning"><strong>意味：</strong>{it['meaning']}</p>
      <p class="c-vocab-card__example"><strong>例文：</strong>{it['example']}</p>
    </div>"""
        cards_html.append(card)

    cards_joined = "\n".join(cards_html)
    box_html = f"""<!-- wp:html -->
<div class="c-vocab-box">
  <h3 class="c-vocab-box__title">🎯 今回の語彙（重要ボキャブラリー）</h3>
  <p class="c-vocab-box__lead">この学習ノートに登場した、覚えておきたい重要日本語：</p>
  <div class="c-vocab-grid">
{cards_joined}
  </div>
</div>
<!-- /wp:html -->"""
    return box_html

for post_id, items in vocab_definitions.items():
    box = generate_box_html(items)
    
    php_code = f"""<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$p = get_post({post_id});
if ($p) {{
    $content = $p->post_content;
    $box_html = {repr(box)};
    
    // Insert before separator or series or at the end
    if (strpos($content, '<!-- wp:separator') !== false) {{
        $parts = explode('<!-- wp:separator', $content, 2);
        $new_content = $parts[0] . "\\n\\n" . $box_html . "\\n\\n<!-- wp:separator" . $parts[1];
    }} elseif (strpos($content, '[oscss_series') !== false) {{
        $parts = explode('[oscss_series', $content, 2);
        $new_content = $parts[0] . "\\n\\n" . $box_html . "\\n\\n[oscss_series" . $parts[1];
    }} else {{
        $new_content = $content . "\\n\\n" . $box_html;
    }}
    
    wp_update_post(array(
        'ID' => {post_id},
        'post_content' => $new_content
    ));
    echo "[UPDATED Post {post_id}] Added c-vocab-box!" . PHP_EOL;
}}
"""
    sftp = ssh.open_sftp()
    with sftp.open('add_vocab_old.php', 'w') as f:
        f.write(php_code)
    sftp.close()

    stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php add_vocab_old.php && rm add_vocab_old.php')
    print(stdout.read().decode('utf-8', errors='replace'))

# Purge cache
stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php -r "require(getenv(\'HOME\') . \'/web/nihongo.oscarchair.jp/wp-load.php\'); if(has_action(\'litespeed_purge_all\')) do_action(\'litespeed_purge_all\'); echo \'Cache purged.\';"')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
