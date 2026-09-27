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
    // Print first 3000 chars of content
    echo substr($p->post_content, 0, 4000);
}
"""

sftp = ssh.open_sftp()
with sftp.open('dump_post_2474.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php dump_post_2474.php && rm dump_post_2474.php')
out = stdout.read().decode('utf-8', errors='replace')
with open('scripts/audit/dump_2474.txt', 'w', encoding='utf-8') as df:
    df.write(out)
print(f"Dumped {len(out)} chars")
ssh.close()
