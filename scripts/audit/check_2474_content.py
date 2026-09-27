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
echo "=== POST 2474 TITLE ===" . PHP_EOL . $p->post_title . PHP_EOL;
echo "=== POST 2474 STATUS ===" . PHP_EOL . $p->post_status . PHP_EOL;
echo "=== POST 2474 CONTENT PREVIEW (first 1000 chars) ===" . PHP_EOL;
echo substr($p->post_content, 0, 1000) . PHP_EOL;

$pos = strpos($p->post_content, 'ゲームオーバー');
echo "=== GAME OVER POS: " . var_export($pos, true) . PHP_EOL;
if ($pos !== false) {
    echo substr($p->post_content, $pos, 1500) . PHP_EOL;
}
"""

sftp = ssh.open_sftp()
with sftp.file('/tmp/check_2474_content.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php /tmp/check_2474_content.php')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
