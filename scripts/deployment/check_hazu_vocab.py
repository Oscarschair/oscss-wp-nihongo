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
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$p = get_page_by_path('japanese-comparing-hazu-vs-wake-nuance-differences', OBJECT, 'post');
if ($p) {
    echo "--- POST TITLE: " . $p->post_title . " ---" . PHP_EOL;
    $pos = strpos($p->post_content, 'c-vocab');
    if ($pos !== false) {
        echo substr($p->post_content, $pos - 30, 6000);
    } else {
        echo "c-vocab not found in content!";
    }
} else {
    echo "Post not found";
}
"""

sftp = ssh.open_sftp()
with sftp.open('check_hazu_vocab.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php check_hazu_vocab.php && rm check_hazu_vocab.php')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
