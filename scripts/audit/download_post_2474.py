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
    file_put_contents('post_2474_full.txt', $p->post_content);
    echo "Saved post_2474_full.txt, size: " . strlen($p->post_content) . PHP_EOL;
}
"""

sftp = ssh.open_sftp()
with sftp.open('dump_full.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php dump_full.php && rm dump_full.php')
print(stdout.read().decode('utf-8', errors='replace'))

sftp = ssh.open_sftp()
sftp.get('post_2474_full.txt', 'scripts/audit/post_2474_full.txt')
sftp.remove('post_2474_full.txt')
sftp.close()
ssh.close()
print("Downloaded post_2474_full.txt successfully!")
