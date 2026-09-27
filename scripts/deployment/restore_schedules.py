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

$schedules = array(
    2472 => array('date' => '2026-10-13 08:00:00', 'gmt' => '2026-10-12 23:00:00'),
    2474 => array('date' => '2026-10-14 08:00:00', 'gmt' => '2026-10-13 23:00:00'),
    2476 => array('date' => '2026-10-15 08:00:00', 'gmt' => '2026-10-14 23:00:00'),
);

foreach ($schedules as $pid => $sched) {
    wp_update_post(array(
        'ID'            => $pid,
        'post_date'     => $sched['date'],
        'post_date_gmt' => $sched['gmt'],
        'post_status'   => 'future'
    ));
    $p = get_post($pid);
    echo "[SCHEDULED RESTORED] Post {$pid} ({$p->post_name}) -> Status: {$p->post_status} | Date: {$p->post_date}" . PHP_EOL;
}

if (has_action('litespeed_purge_all')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache Purged All!" . PHP_EOL;
}
"""

sftp = ssh.open_sftp()
with sftp.file('/tmp/restore_schedule.php', 'w') as f:
    f.write(php_code)
sftp.close()

print("Restoring correct publication schedules...")
stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php /tmp/restore_schedule.php')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))
ssh.close()
print("Schedules restored successfully!")
