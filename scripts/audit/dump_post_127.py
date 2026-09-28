import paramiko
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

sftp = ssh.open_sftp()
test_php = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$p = get_post(127);
echo "POST ID: " . $p->ID . "\\n";
echo "CONTENT LENGTH: " . strlen($p->post_content) . "\\n";
echo "FIRST 500 CHARS:\\n" . mb_substr($p->post_content, 0, 500, 'UTF-8') . "\\n";
"""
with sftp.open('dump_127.php', 'w') as f:
    f.write(test_php)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php dump_127.php && rm dump_127.php')
out = stdout.read().decode('utf-8', errors='replace')
print(out)
ssh.close()
