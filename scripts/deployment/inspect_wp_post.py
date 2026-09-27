import sys
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

php_code = """<?php
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
$ids = [1, 19, 30, 36, 44, 85, 109, 111, 127, 144, 150];
foreach ($ids as $id) {
    $p = get_post($id);
    if ($p) {
        $clean_len = mb_strlen(strip_tags($p->post_content));
        echo "ID {$id} | len: " . strlen($p->post_content) . " | text: {$clean_len}字 | " . mb_substr($p->post_title, 0, 30) . "\\n";
    }
}
"""

sftp = ssh.open_sftp()
with sftp.open('inspect_wp_posts.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php inspect_wp_posts.php && rm inspect_wp_posts.php')
out = stdout.read().decode('utf-8', errors='replace')
print(out)
ssh.close()
