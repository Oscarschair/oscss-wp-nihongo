import paramiko
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

php_code = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$p = get_post(2474);
if (strpos($p->post_content, 'c-dungeon-route') !== false) {
    echo "SUCCESS: Post 2474 contains c-dungeon-route!\n";
} else {
    echo "Post 2474 DOES NOT contain c-dungeon-route.\n";
    // Check if there is still pre block
    if (strpos($p->post_content, '黄金攻略ルート') !== false) {
        $pos = strpos($p->post_content, '黄金攻略ルート');
        echo substr($p->post_content, $pos - 20, 800) . "\n";
    }
}
"""

sftp = ssh.open_sftp()
with sftp.open('check_route.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php check_route.php && rm check_route.php')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
