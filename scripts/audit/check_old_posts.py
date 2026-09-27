import paramiko
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

php_check = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$ids = array(1, 19, 30, 36, 85, 109, 111, 127, 144, 150);
foreach ($ids as $id) {
    $p = get_post($id);
    if ($p) {
        $has_vocab = (strpos($p->post_content, '語彙') !== false || strpos($p->post_content, 'ボキャブラリー') !== false);
        echo "[" . $id . "] " . $p->post_title . " -> Has vocab keyword? " . ($has_vocab ? "YES" : "NO") . PHP_EOL;
    }
}
"""

sftp = ssh.open_sftp()
with sftp.open('check_old.php', 'w') as f:
    f.write(php_check)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php check_old.php && rm check_old.php')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
