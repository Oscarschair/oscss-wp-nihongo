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

$pid = 3156;
$post = get_post($pid);
$thumb_id = get_post_thumbnail_id($pid);
echo "Post ID: " . $pid . PHP_EOL;
echo "Thumb ID: " . $thumb_id . PHP_EOL;
echo "Has thumb: " . (has_post_thumbnail($pid) ? "YES" : "NO") . PHP_EOL;

$thumb_html = get_the_post_thumbnail($pid, 'full');
echo "Thumb HTML: " . $thumb_html . PHP_EOL;
"""

with sftp.open('test_thumb_html.php', 'w') as f:
    f.write(php_code)

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php test_thumb_html.php && rm test_thumb_html.php')
print(stdout.read().decode('utf-8'))
print('STDERR:', stderr.read().decode('utf-8'))
sftp.close()
ssh.close()
