import paramiko
import sys
import re

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

$posts = get_posts(array(
    'post_type' => 'post',
    'post_status' => 'any',
    'numberposts' => -1
));

foreach ($posts as $p) {
    if (preg_match_all('/<p class="c-vocab-card__example"><strong>例文[：:]<\\/strong>(.*?)<\\/p>/s', $p->post_content, $m)) {
        foreach ($m[1] as $ex) {
            $raw = trim(strip_tags($ex));
            if (strpos($raw, '##') !== false || strpos($raw, '|') !== false || strpos($raw, '」') === 0 || strpos($raw, '➔') !== false || strlen($raw) < 5) {
                echo "[DIRTY EX Post {$p->ID}] {$p->post_title}" . PHP_EOL;
                echo "   " . $raw . PHP_EOL;
            }
        }
    }
}
"""

sftp = ssh.open_sftp()
with sftp.open('check_dirty_examples.php', 'w') as f:
    f.write(php_check)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php check_dirty_examples.php && rm check_dirty_examples.php')
out = stdout.read().decode('utf-8', errors='replace')
print(out)
ssh.close()
