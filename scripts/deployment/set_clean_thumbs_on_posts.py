import paramiko
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

php_code = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$mapping = array(
    1621 => 1632, // 10/7 delivery -> clean thumb
    1625 => 1633, // 10/9 hanko -> clean thumb
    1631 => 1634, // 10/12 expiry -> clean thumb
);

foreach ($mapping as $post_id => $thumb_id) {
    set_post_thumbnail($post_id, $thumb_id);
    clean_post_cache($post_id);
    echo "Set post {$post_id} thumbnail to {$thumb_id}\n";
}

if (function_exists('opcache_reset')) { opcache_reset(); }
if (class_exists('LiteSpeed\\Purge')) { LiteSpeed\\Purge::purge_all(); }
echo "Thumbnails updated and caches purged!\n";
"""

with sftp.open('set_clean_post_thumbs.php', 'w') as f:
    f.write(php_code)

stdin, stdout, stderr = ssh.exec_command('LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php set_clean_post_thumbs.php && rm set_clean_post_thumbs.php')
out = stdout.read().decode('utf-8')
print(out)
