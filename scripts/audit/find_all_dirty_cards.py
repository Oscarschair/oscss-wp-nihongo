import paramiko
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

php = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$posts = get_posts(array(
    'post_type' => 'post',
    'post_status' => 'any',
    'numberposts' => -1
));

foreach ($posts as $p) {
    if (strpos($p->post_content, 'c-vocab-card') !== false) {
        // extract all cards
        if (preg_match_all('/<div class="c-vocab-card">.*?<\\/div>/s', $p->post_content, $m)) {
            foreach ($m[0] as $c) {
                if (strpos($c, '##') !== false || strpos($c, '|') !== false || strpos($c, '」') !== false || strpos($c, '│') !== false) {
                    echo "[DIRTY POST {$p->ID}] {$p->post_title}" . PHP_EOL;
                    echo "CARD: " . strip_tags($c) . PHP_EOL;
                }
            }
        }
    }
}
"""

sftp = ssh.open_sftp()
with sftp.open('find_all_dirty.php', 'w') as f:
    f.write(php)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php find_all_dirty.php && rm find_all_dirty.php')
out = stdout.read().decode('utf-8', errors='replace')
with open('scripts/audit/dirty_cards_report.txt', 'w', encoding='utf-8') as rf:
    rf.write(out)
print(f"Report written ({len(out)} chars)")
ssh.close()
