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

$posts = get_posts(array(
    'post_type' => 'post',
    'post_status' => 'any',
    'numberposts' => -1
));

$has_vocab_box = 0;
$no_vocab_box = 0;
$missing_posts = array();

foreach ($posts as $p) {
    if (strpos($p->post_content, 'c-vocab-box') !== false) {
        $has_vocab_box++;
    } else {
        $no_vocab_box++;
        $missing_posts[] = array('id' => $p->ID, 'title' => $p->post_title);
    }
}

echo "Posts with c-vocab-box: " . $has_vocab_box . PHP_EOL;
echo "Posts WITHOUT c-vocab-box: " . $no_vocab_box . PHP_EOL;
echo "Missing list:" . PHP_EOL;
foreach ($missing_posts as $mp) {
    echo "  - [" . $mp['id'] . "] " . $mp['title'] . PHP_EOL;
}
"""

sftp = ssh.open_sftp()
with sftp.open('check_vocab_box.php', 'w') as f:
    f.write(php_check)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php check_vocab_box.php && rm check_vocab_box.php')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
