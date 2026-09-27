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

$now = current_time('mysql');
$now_gmt = current_time('mysql', 1);

foreach (array(2472, 2474, 2476) as $pid) {
    wp_update_post(array(
        'ID' => $pid,
        'post_status' => 'publish',
        'post_date' => $now,
        'post_date_gmt' => $now_gmt
    ));
    $p = get_post($pid);
    echo "[PUBLISHED] Post {$pid} ({$p->post_name}) Status: {$p->post_status} Date: {$p->post_date}" . PHP_EOL;
}

if (has_action('litespeed_purge_all')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache Purged All!" . PHP_EOL;
}
"""

sftp = ssh.open_sftp()
with sftp.file('/tmp/publish_all.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php /tmp/publish_all.php')
print(stdout.read().decode('utf-8'))
ssh.close()
