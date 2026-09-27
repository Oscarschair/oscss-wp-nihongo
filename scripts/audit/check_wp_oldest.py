import paramiko
import time

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

php_script = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$posts = get_posts(array(
    'post_type' => 'post',
    'post_status' => 'publish',
    'orderby' => 'date',
    'order' => 'ASC',
    'numberposts' => 15
));

echo "=== WordPress 最古順の投稿一覧 ===" . PHP_EOL;
foreach ($posts as $p) {
    echo sprintf("[%d] %s | %s (%s)", $p->ID, $p->post_date, $p->post_title, $p->post_name) . PHP_EOL;
}
"""

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], timeout=10)
    sftp = ssh.open_sftp()
    with sftp.open('list_oldest.php', 'w') as f:
        f.write(php_script)
    stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php list_oldest.php && rm list_oldest.php')
    print(stdout.read().decode('utf-8', errors='replace'))
    sftp.close()
    ssh.close()
except Exception as e:
    print(f"SSH Error: {e}")
