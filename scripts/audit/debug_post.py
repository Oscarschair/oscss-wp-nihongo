import paramiko

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

php_check = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$p = get_post(2472);
$content = strip_shortcodes( $p->post_content );
$content_no_rt = preg_replace( '/<rt>.*?<\\/rt>/su', '', $content );
$pure = wp_strip_all_tags( $content_no_rt );
$pure = preg_replace( '/\\s+/', '', $pure );

echo "Raw content length: " . strlen($p->post_content) . PHP_EOL;
echo "Pure text sample: " . mb_substr($pure, 0, 100, 'UTF-8') . "..." . PHP_EOL;
echo "Pure text end: " . mb_substr($pure, -100, null, 'UTF-8') . PHP_EOL;
echo "Pure length: " . mb_strlen($pure, 'UTF-8') . PHP_EOL;
"""

sftp = ssh.open_sftp()
with sftp.open('debug_post.php', 'w') as f:
    f.write(php_check)

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php debug_post.php && rm debug_post.php')
print(stdout.read().decode('utf-8', errors='replace'))

sftp.close()
ssh.close()
