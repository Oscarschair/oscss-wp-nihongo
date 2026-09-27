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
$posts = $wpdb->get_results("SELECT ID, post_status, post_title FROM {$wpdb->posts} WHERE post_type = 'post' ORDER BY ID ASC LIMIT 10");
foreach ($posts as $p) {
    echo $p->ID . " | " . $p->post_status . " | " . $p->post_title . PHP_EOL;
}
"""

sftp = ssh.open_sftp()
with sftp.file('/tmp/check_titles.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php /tmp/check_titles.php')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))
ssh.close()
