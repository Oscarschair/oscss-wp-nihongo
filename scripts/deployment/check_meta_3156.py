import paramiko

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

php_code = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$p = get_post(3156);
echo "Post Title: " . $p->post_title . PHP_EOL;
echo "Post Status: " . $p->post_status . PHP_EOL;
$thumb_id = get_post_thumbnail_id(3156);
echo "Thumb ID: " . $thumb_id . PHP_EOL;
$thumb_meta = wp_get_attachment_metadata($thumb_id);
print_r($thumb_meta);
"""

with sftp.open('check_meta_3156.php', 'w') as f:
    f.write(php_code)

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php check_meta_3156.php && rm check_meta_3156.php')
print(stdout.read().decode('utf-8'))
print('STDERR:', stderr.read().decode('utf-8'))
sftp.close()
ssh.close()
