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

cmd = """/usr/local/php/8.2/bin/php -r "require 'web/nihongo.oscarchair.jp/wp-load.php'; foreach(array(2472, 2474, 2476, 2721) as \$id) { \$p = get_post(\$id); if(\$p) echo \$p->ID . ' | ' . \$p->post_status . ' | ' . \$p->post_date . ' | ' . \$p->post_name . ' | ' . \$p->post_title . PHP_EOL; }" """

stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))
ssh.close()
