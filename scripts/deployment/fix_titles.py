import os
import sys
import re
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

def clean_ruby(text):
    # <ruby>漢字<rt>かんじ</rt></ruby> -> 漢字
    text = re.sub(r'<ruby>(.*?)<rt>.*?</rt></ruby>', r'\1', text)
    # 残りのHTMLタグ除去
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

posts = [
    (2472, "content/posts/2026-10-13-kotoba-no-aya-is-shouchidesu-wrong-business-japanese-trap.md"),
    (2474, "content/posts/2026-10-14-street-japanese-city-hall-resident-registration-dungeon-guide.md"),
    (2476, "content/posts/2026-10-15-japanese-comparing-rashii-souda-youda-differences.md"),
]

updates = []
for pid, md_path in posts:
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    m = re.search(r'^title:\s*["\']?(.*?)["\']?$', content, re.MULTILINE)
    raw_title = m.group(1) if m else ""
    cleaned = clean_ruby(raw_title)
    updates.append((pid, cleaned))
    print(f"Post {pid} Clean Title: {cleaned}")

# PHP スクリプト生成
php_code = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$titles = array(
"""
for pid, title in updates:
    safe_title = title.replace("'", "\\'")
    php_code += f"    {pid} => '{safe_title}',\n"

php_code += """
);

foreach ($titles as $pid => $title) {
    wp_update_post(array(
        'ID' => $pid,
        'post_title' => $title
    ));
    $p = get_post($pid);
    echo "[UPDATED TITLE] Post {$pid}: " . $p->post_title . PHP_EOL;
}

if (has_action('litespeed_purge_all')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache Purged All!" . PHP_EOL;
}
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
with sftp.file('/tmp/fix_titles.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php /tmp/fix_titles.php')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))
ssh.close()
