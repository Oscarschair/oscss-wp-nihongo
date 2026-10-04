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
$thumb_id = get_post_thumbnail_id($pid);
echo "Thumb ID: " . $thumb_id . PHP_EOL;
$url = wp_get_attachment_url($thumb_id);
echo "URL: " . $url . PHP_EOL;
$file = get_attached_file($thumb_id);
echo "File: " . $file . PHP_EOL;
echo "File exists? " . (file_exists($file) ? "YES" : "NO") . PHP_EOL;

// Also check post content images
$p = get_post($pid);
preg_match_all('/<img[^>]+src="([^"]+)"/', $p->post_content, $matches);
echo "Content images:" . PHP_EOL;
foreach ($matches[1] as $src) {
    echo "  src: " . $src . PHP_EOL;
}
"""

with sftp.open('debug_post_3156.php', 'w') as f:
    f.write(php_code)

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php debug_post_3156.php && rm debug_post_3156.php')
print(stdout.read().decode('utf-8'))
print('STDERR:', stderr.read().decode('utf-8'))
sftp.close()
ssh.close()
