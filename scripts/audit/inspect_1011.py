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
    's' => 'はず',
    'numberposts' => 5
));

foreach ($posts as $p) {
    echo "Found Post ID: " . $p->ID . " - " . $p->post_name . " - " . $p->post_title . PHP_EOL;
    $pos = strpos($p->post_content, 'c-vocab-box');
    if ($pos !== false) {
        echo substr($p->post_content, $pos - 20, 1500) . PHP_EOL;
    }
}
"""

sftp = ssh.open_sftp()
with sftp.open('find_1011_f.php', 'w') as f:
    f.write(php)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php find_1011_f.php && rm find_1011_f.php')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
