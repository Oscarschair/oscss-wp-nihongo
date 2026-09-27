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
if ($p) {
    echo "Post 2474 found, length: " . strlen($p->post_content) . PHP_EOL;
    $pos = strpos($p->post_content, '黄金');
    echo "pos of 黄金: " . var_export($pos, true) . PHP_EOL;
    if ($pos !== false) {
        echo substr($p->post_content, $pos - 100, 1500) . PHP_EOL;
    }
}
"""

sftp = ssh.open_sftp()
with sftp.open('check_route_raw.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php check_route_raw.php && rm check_route_raw.php')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
