import os
import sys
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

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

php_code = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

global $wpdb;
$rows = $wpdb->get_results("SELECT ID, post_status, post_title, post_name FROM {$wpdb->posts} WHERE post_content LIKE '%必須装備%' OR post_content LIKE '%ゲームオーバー%' OR post_title LIKE '%市役所%'");
foreach ($rows as $r) {
    echo $r->ID . ' | ' . $r->post_status . ' | ' . $r->post_name . ' | ' . $r->post_title . PHP_EOL;
}
"""

sftp = ssh.open_sftp()
with sftp.file('/tmp/find_post.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php /tmp/find_post.php')
print(stdout.read().decode('utf-8'))
ssh.close()
