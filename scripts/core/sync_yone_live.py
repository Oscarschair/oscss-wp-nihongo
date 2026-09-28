import paramiko
import sys
import os
import re

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.abspath(os.getcwd()))
from scripts.core.gutenberg_parser import parse_markdown_to_gutenberg_full

post_path = 'content/posts/2026-09-05-kotoba-no-aya-how-to-use-the-final-particle-yone-for-smooth-conversation.md'
gutenberg_html = parse_markdown_to_gutenberg_full(post_path)

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

# ローカルの一時ファイルにUTF-8で保存してからsftp.put
temp_local = 'temp_yone_gutenberg.html'
with open(temp_local, 'w', encoding='utf-8') as f:
    f.write(gutenberg_html)

sftp = ssh.open_sftp()
sftp.put(temp_local, 'temp_yone_body.txt')
os.remove(temp_local)

remote_php = f"""<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$body = file_get_contents('temp_yone_body.txt');

// MarkdownをHTML段落に整流
$post_id = 127;
wp_update_post(array(
    'ID' => $post_id,
    'post_content' => $body
));

$p = get_post($post_id);
$calc_content = strip_shortcodes($p->post_content);
$calc_content = preg_replace('/<rt>.*?<\\/rt>/su', '', $calc_content);
$calc_content = wp_strip_all_tags($calc_content);
$calc_content = preg_replace('/\\s+/', '', $calc_content);
$chars = mb_strlen($calc_content, 'UTF-8');
$mins = (int) ceil($chars / 500);

echo "Updated Post ID: " . $post_id . PHP_EOL;
echo "Live Chars: " . $chars . " chars" . PHP_EOL;
echo "Live Reading Time: " . $mins . " mins" . PHP_EOL;

if (has_action('litespeed_purge_all')) {{
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache Purged All!" . PHP_EOL;
}}
"""

with sftp.open('update_yone.php', 'w') as f:
    f.write(remote_php)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php update_yone.php && rm update_yone.php temp_yone_body.txt')
out = stdout.read().decode('utf-8', errors='replace')
print(out)
ssh.close()
