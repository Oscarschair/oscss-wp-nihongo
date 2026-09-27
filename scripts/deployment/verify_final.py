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

$posts = get_posts(array('numberposts' => -1, 'post_status' => 'any'));
$bad = 0;

foreach ($posts as $p) {
    $c = $p->post_content;
    $cards = substr_count($c, 'c-vocab-card__example');
    if ($cards !== 3) {
        echo "Card count != 3: Post " . $p->ID . " (" . $p->post_name . ") count=" . $cards . PHP_EOL;
        $bad++;
    }
    if (strpos($c, '】・合点') !== false || strpos($c, '## 1.') !== false || strpos($c, '例文：」') !== false) {
        echo "Corrupted symbols found in Post " . $p->ID . PHP_EOL;
        $bad++;
    }
}

if ($bad === 0) {
    echo "SUCCESS: ALL 52 POSTS 100% CLEAN AND PERFECT! No corrupted symbols or extra cards." . PHP_EOL;
} else {
    echo "Found " . $bad . " issues." . PHP_EOL;
}
"""

sftp = ssh.open_sftp()
with sftp.open('verify_final.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php verify_final.php && rm verify_final.php')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
