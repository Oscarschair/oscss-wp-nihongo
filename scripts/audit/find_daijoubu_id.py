import paramiko

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False, timeout=10)

php_find = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$posts = get_posts(array(
    'post_type' => 'post',
    'name' => 'kotoba-no-aya-the-trap-of-daijoubu-yes-or-no-japanese-magic-phrase',
    'post_status' => 'any',
    'numberposts' => 1
));

if (!empty($posts)) {
    echo "FOUND_ID: " . $posts[0]->ID . " | Title: " . $posts[0]->post_title . PHP_EOL;
} else {
    echo "NOT_FOUND" . PHP_EOL;
}
"""

sftp = ssh.open_sftp()
with sftp.open('find_id.php', 'w') as f:
    f.write(php_find)

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php find_id.php && rm find_id.php')
print(stdout.read().decode('utf-8', errors='replace'))

sftp.close()
ssh.close()
