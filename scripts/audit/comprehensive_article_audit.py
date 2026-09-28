import paramiko
import json
import sys
import os
import glob
import re

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 1. ローカル記事の調査
local_files = sorted(glob.glob('content/posts/*.md'))
local_data = {}

for f in local_files:
    fname = os.path.basename(f)
    slug = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', fname).replace('.md', '')
    with open(f, 'r', encoding='utf-8') as fp:
        raw = fp.read()
    
    # frontmatter除去
    body = re.sub(r'^---.*?---\s*', '', raw, flags=re.DOTALL)
    
    # 語彙ボックスチェック
    has_vocab_box = ('c-vocab-box' in body)
    has_vocab_heading = bool(re.search(r'#+\s*🎯?\s*(?:今回の語彙|重要ボキャブラリー|ボキャブラリー)', body))
    
    # ルビチェック
    ruby_count = len(re.findall(r'<ruby>', body))
    
    # 文字数（タグ・ルビrt・空白除去）
    c = re.sub(r'<rt>.*?</rt>', '', body, flags=re.DOTALL)
    c = re.sub(r'<[^>]+>', '', c)
    c = re.sub(r'\s+', '', c)
    char_count = len(c)
    est_mins = (char_count + 499) // 500
    
    local_data[slug] = {
        'file': fname,
        'chars': char_count,
        'est_mins': est_mins,
        'has_vocab_box': has_vocab_box,
        'has_vocab_heading': has_vocab_heading,
        'ruby_count': ruby_count
    }

print(f"Loaded {len(local_data)} local markdown posts.")

# 2. 本番WordPress記事の調査
with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

remote_script = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$posts = get_posts(array(
    'post_type' => 'post',
    'post_status' => 'publish',
    'numberposts' => -1,
    'orderby' => 'date',
    'order' => 'ASC'
));

$results = array();

foreach ($posts as $p) {
    $content = $p->post_content;
    $slug = $p->post_name;
    
    // 文字数算出（テーマの oscss_get_reading_time と同等）
    $calc_content = strip_shortcodes($content);
    $calc_content = preg_replace('/<rt>.*?<\\/rt>/su', '', $calc_content);
    $calc_content = wp_strip_all_tags($calc_content);
    $calc_content = preg_replace('/\\s+/', '', $calc_content);
    $chars = mb_strlen($calc_content, 'UTF-8');
    $mins = (int) ceil($chars / 500);
    
    // 語彙
    $has_vocab_box = (strpos($content, 'c-vocab-box') !== false);
    $has_vocab_heading = (bool) preg_match('/(?:語彙|ボキャブラリー)/u', $content);
    
    // ルビ数
    $ruby_count = preg_match_all('/<ruby>/u', $content, $rm);
    
    $results[$slug] = array(
        'id' => $p->ID,
        'title' => $p->post_title,
        'date' => $p->post_date,
        'chars' => $chars,
        'mins' => $mins,
        'has_vocab_box' => $has_vocab_box,
        'has_vocab_heading' => $has_vocab_heading,
        'ruby_count' => $ruby_count
    );
}

echo json_encode($results, JSON_UNESCAPED_UNICODE);
"""

sftp = ssh.open_sftp()
with sftp.open('audit_all_posts.php', 'w') as f:
    f.write(remote_script)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php audit_all_posts.php && rm audit_all_posts.php')
out = stdout.read().decode('utf-8', errors='replace')
ssh.close()

try:
    wp_data = json.loads(out)
except Exception as e:
    print("Failed to parse JSON from remote:", e)
    print("Output was:", out[:500])
    sys.exit(1)

print(f"Retrieved {len(wp_data)} posts from WordPress Live.\n")

# 3. 突合・診断レポート
short_posts = []
no_vocab_box = []
no_ruby = []
mismatch_posts = []

print(f"{'Slug':<50} | {'WP分':<4} | {'WP文字':<6} | {'BOX':<4} | {'WPルビ':<5} | {'MD分':<4} | {'MD文字':<6} | {'MDルビ':<5}")
print("-" * 105)

for slug, wp in wp_data.items():
    loc = local_data.get(slug, {})
    wp_mins = wp['mins']
    wp_chars = wp['chars']
    wp_box = 'OK' if wp['has_vocab_box'] else 'NG'
    wp_ruby = wp['ruby_count']
    
    md_mins = loc.get('est_mins', '-')
    md_chars = loc.get('chars', '-')
    md_ruby = loc.get('ruby_count', '-')
    
    if wp_mins < 7:
        short_posts.append((slug, wp['id'], wp['title'], wp_mins, wp_chars))
    if not wp['has_vocab_box']:
        no_vocab_box.append((slug, wp['id'], wp['title']))
    if wp_ruby < 10:
        no_ruby.append((slug, wp['id'], wp['title'], wp_ruby))
    
    # ローカルと本番の文字数乖離（500字以上差がある場合）
    if loc and abs(wp_chars - loc['chars']) > 500:
        mismatch_posts.append((slug, wp_chars, loc['chars']))
        
    print(f"{slug[:48]:<50} | {wp_mins:<4} | {wp_chars:<6} | {wp_box:<4} | {wp_ruby:<5} | {md_mins:<4} | {md_chars:<6} | {md_ruby:<5}")

print("\n" + "=" * 80)
print(f"【監査結果サマリー】 (本番公開記事数: {len(wp_data)})")
print(f"1. 読了目安7分未満（短い・未拡充記事）: {len(short_posts)} 件")
for s, pid, title, m, c in short_posts:
    print(f"   - [ID {pid}] 約{m}分 ({c}文字): {s} ({title})")

print(f"\n2. 語彙カードBOX（c-vocab-box）欠落記事: {len(no_vocab_box)} 件")
for s, pid, title in no_vocab_box:
    print(f"   - [ID {pid}]: {s}")

print(f"\n3. ルビ極小（< 10件）記事: {len(no_ruby)} 件")
for s, pid, title, r in no_ruby:
    print(f"   - [ID {pid}] (ルビ{r}個): {s}")

print(f"\n4. ローカルMarkdownとWordPress本番の乖離（500文字以上差）: {len(mismatch_posts)} 件")
for s, wc, lc in mismatch_posts:
    print(f"   - {s}: 本番={wc}字 vs ローカル={lc}字 (差={wc - lc})")
