import os
import re
import sys
import base64
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

from scripts.core.gutenberg_parser import parse_markdown_to_gutenberg_full

posts = [
    (2472, "content/posts/2026-10-13-kotoba-no-aya-is-shouchidesu-wrong-business-japanese-trap.md"),
    (2474, "content/posts/2026-10-14-street-japanese-city-hall-resident-registration-dungeon-guide.md"),
    (2476, "content/posts/2026-10-15-japanese-comparing-rashii-souda-youda-differences.md"),
]

post_payloads = []
for pid, md_path in posts:
    gutenberg_html = parse_markdown_to_gutenberg_full(md_path)
    b64 = base64.b64encode(gutenberg_html.encode('utf-8')).decode('ascii')
    post_payloads.append((pid, b64))

php_code = f"""<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$updates = array(
    2472 => '{post_payloads[0][1]}',
    2474 => '{post_payloads[1][1]}',
    2476 => '{post_payloads[2][1]}'
);

foreach ($updates as $pid => $b64) {{
    $content = base64_decode($b64);
    wp_update_post(array(
        'ID' => $pid,
        'post_content' => $content,
        'post_status' => 'publish'
    ));
    $p = get_post($pid);
    $time = function_exists('oscss_get_reading_time') ? oscss_get_reading_time($p) : 'N/A';
    echo "[UPDATED WITH VOCAB & TABLES] Post " . $pid . ": " . $p->post_title . " | Reading time: 約" . $time . "分 (" . strlen($content) . " bytes)" . PHP_EOL;
}}

if (has_action('litespeed_purge_all')) {{
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache Purged All!" . PHP_EOL;
}}
"""

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    env['SSH_HOST'], 
    int(env['SSH_PORT']), 
    env['SSH_USER'], 
    env['SSH_PASS'], 
    timeout=15,
    look_for_keys=False,
    allow_agent=False
)

sftp = ssh.open_sftp()
with sftp.file('/tmp/sync_vocab.php', 'w') as f:
    f.write(php_code)
sftp.close()

print("Executing sync with vocab & tables...")
stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php /tmp/sync_vocab.php')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))
ssh.close()
print("All synced successfully!")
