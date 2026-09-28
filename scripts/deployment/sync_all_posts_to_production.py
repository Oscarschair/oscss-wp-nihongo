# -*- coding: utf-8 -*-
import paramiko
import sys
import os
import glob
import re
import json

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.abspath(os.getcwd()))
from scripts.core.gutenberg_parser import parse_markdown_to_gutenberg_full

print("=== 1. 全MarkdownファイルをGutenbergブロックHTMLへ一括パース ===")
files = sorted(glob.glob('content/posts/*.md'))
posts_payload = {}

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        raw_text = fp.read()
    
    # get slug
    slug_match = re.search(r'slug:\s*([^\s\n\r]+)', raw_text)
    if slug_match:
        slug = slug_match.group(1).strip('"\'')
    else:
        base = os.path.basename(f)
        slug = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', base).replace('.md', '')
    
    gutenberg_html = parse_markdown_to_gutenberg_full(f)
    posts_payload[slug] = gutenberg_html
    print(f"Parsed: {slug} ({len(gutenberg_html)} chars)")

print(f"\n合計 {len(posts_payload)} 件の投稿をパース完了。")

# ローカル一時ファイルにJSON保存
temp_json = 'temp_all_posts_payload.json'
with open(temp_json, 'w', encoding='utf-8') as f:
    json.dump(posts_payload, f, ensure_ascii=False)

print("\n=== 2. SFTP経由でサーバーへペイロードを転送 ===")
with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

sftp = ssh.open_sftp()
sftp.put(temp_json, 'temp_all_posts_payload.json')
os.remove(temp_json)
print("アップロード完了。")

print("\n=== 3. リモートWordPressで全記事一括更新 (Single Source of Truth 確定) ===")
remote_php = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$json_str = file_get_contents('temp_all_posts_payload.json');
$payload = json_decode($json_str, true);

$posts = get_posts(array(
    'post_type' => 'post',
    'post_status' => 'any',
    'numberposts' => -1
));

$updated_count = 0;
$skipped_count = 0;

foreach ($posts as $p) {
    $slug = $p->post_name;
    if (!isset($payload[$slug])) {
        $skipped_count++;
        continue;
    }
    
    $new_body = $payload[$slug];
    
    wp_update_post(array(
        'ID' => $p->ID,
        'post_content' => $new_body
    ));
    
    $calc_content = strip_shortcodes($new_body);
    $calc_content = preg_replace('/<rt>.*?<\\/rt>/su', '', $calc_content);
    $calc_content = wp_strip_all_tags($calc_content);
    $calc_content = preg_replace('/\\s+/', '', $calc_content);
    $chars = mb_strlen($calc_content, 'UTF-8');
    $mins = (int) ceil($chars / 500);
    
    $has_vocab = (strpos($new_body, 'c-vocab-box') !== false) ? 'YES' : 'NO';
    $ruby_count = substr_count($new_body, '<ruby>');
    
    echo sprintf("[UPDATED] ID: %-4d | Slug: %-45s | Chars: %-5d | Time: 約%2d分 | Vocab: %s | Rubies: %3d\\n",
        $p->ID, substr($slug, 0, 45), $chars, $mins, $has_vocab, $ruby_count
    );
    
    $updated_count++;
}

echo PHP_EOL . "Total Updated: " . $updated_count . " posts, Skipped: " . $skipped_count . PHP_EOL;

if (has_action('litespeed_purge_all')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache: All Purged Successfully!" . PHP_EOL;
}
if (function_exists('wp_cache_flush')) {
    wp_cache_flush();
    echo "WP Object Cache: Flushed!" . PHP_EOL;
}
"""

with sftp.open('sync_all_posts.php', 'w') as f:
    f.write(remote_php)

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php sync_all_posts.php')
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print(out)
if err.strip():
    print("ERR:", err)

# Cleanup remote files
try:
    sftp.remove('temp_all_posts_payload.json')
    sftp.remove('sync_all_posts.php')
except Exception:
    pass

sftp.close()
ssh.close()
print("=== 本番WordPress全記事完全同期 完了 ===")
