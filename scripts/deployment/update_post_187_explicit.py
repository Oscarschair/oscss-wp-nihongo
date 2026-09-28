# -*- coding: utf-8 -*-
import paramiko
import os
import sys

sys.path.insert(0, os.path.abspath('.'))
from scripts.core.gutenberg_parser import parse_markdown_to_gutenberg_full

md_path = 'content/posts/2026-09-11-street-japanese-hair-salon-survival-shampoo-trap-guide.md'
html = parse_markdown_to_gutenberg_full(md_path)

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

temp_file = 'temp_187.html'
with open(temp_file, 'w', encoding='utf-8') as f:
    f.write(html)

sftp = ssh.open_sftp()
sftp.put(temp_file, 'temp_187.html')
os.remove(temp_file)

php = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$content = file_get_contents('temp_187.html');
$res = wp_update_post(array(
    'ID' => 187,
    'post_content' => $content
));

if (is_wp_error($res)) {
    echo "ERROR: " . $res->get_error_message() . PHP_EOL;
} else {
    echo "Post 187 successfully updated!" . PHP_EOL;
}

if (has_action('litespeed_purge_post')) {
    do_action('litespeed_purge_post', 187);
}
if (has_action('litespeed_purge_all')) {
    do_action('litespeed_purge_all');
}
if (function_exists('wp_cache_flush')) {
    wp_cache_flush();
}
echo "Purged all caches!" . PHP_EOL;
"""

with sftp.open('update_187.php', 'w') as f:
    f.write(php)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php update_187.php && rm update_187.php temp_187.html')
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("OUT:", out)
if err:
    print("ERR:", err)
ssh.close()
