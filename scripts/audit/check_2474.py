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

$p = get_post(2474);
echo "Post ID: " . $p->ID . PHP_EOL;
echo "Post Status: " . $p->post_status . PHP_EOL;
echo "Post Date: " . $p->post_date . PHP_EOL;

$pos = strpos($p->post_content, '装備品');
if ($pos !== false) {
    echo "=== AROUND 装備品 ===" . PHP_EOL;
    echo substr($p->post_content, max(0, $pos - 100), 500) . PHP_EOL;
} else {
    echo "NOT FOUND 装備品 in 2474" . PHP_EOL;
}
"""

sftp = ssh.open_sftp()
with sftp.file('/tmp/check_2474.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php /tmp/check_2474.php')
print(stdout.read().decode('utf-8'))
ssh.close()
