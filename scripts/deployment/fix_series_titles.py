import os
import sys
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

# 1. ローカルのMarkdown正本のタイトルを修正
fp14 = 'content/posts/2026-10-14-street-japanese-city-hall-resident-registration-dungeon-guide.md'
with open(fp14, 'r', encoding='utf-8') as f:
    c14 = f.read()
c14 = c14.replace('title: "ストリート日本語：', 'title: "街角サバイバル：')
with open(fp14, 'w', encoding='utf-8') as f:
    f.write(c14)
print("Updated local 10-14 markdown title")

fp15 = 'content/posts/2026-10-15-japanese-comparing-rashii-souda-youda-differences.md'
with open(fp15, 'r', encoding='utf-8') as f:
    c15 = f.read()
c15 = c15.replace('title: "日本語比べ：', 'title: "くらべてみました：')
with open(fp15, 'w', encoding='utf-8') as f:
    f.write(c15)
print("Updated local 10-15 markdown title")

# 2. WordPress 本番 DB のタイトルを修正
title14 = "街角サバイバル：市役所の「住民登録・転入届」ダンジョン完全攻略ガイド｜受付・書類・窓口神フレーズと落とし穴"
title15 = "くらべてみました：【徹底比較】「そうだ」「らしい」「ようだ」の使い分け完全マスター｜推量・伝聞のニュアンスと五感の罠"

php_code = f"""<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

wp_update_post(array(
    'ID' => 2474,
    'post_title' => '{title14}'
));

wp_update_post(array(
    'ID' => 2476,
    'post_title' => '{title15}'
));

$p14 = get_post(2474);
$p15 = get_post(2476);
echo "[TITLE FIXED] 2474: " . $p14->post_title . PHP_EOL;
echo "[TITLE FIXED] 2476: " . $p15->post_title . PHP_EOL;

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
with sftp.file('/tmp/fix_series_titles.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php /tmp/fix_series_titles.php')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))
ssh.close()
print("Series titles updated successfully!")
