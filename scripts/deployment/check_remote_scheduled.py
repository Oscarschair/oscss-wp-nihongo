# -*- coding: utf-8 -*-
import paramiko
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    hostname=env['SSH_HOST'],
    port=int(env['SSH_PORT']),
    username=env['SSH_USER'],
    password=env['SSH_PASS'],
    look_for_keys=False,
    allow_agent=False,
    timeout=30
)

php_code = """
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
$posts = get_posts([
    'post_status' => 'future',
    'numberposts' => 30,
    'orderby' => 'date',
    'order' => 'ASC'
]);
echo "Future scheduled posts count: " . count($posts) . PHP_EOL;
foreach ($posts as $p) {
    $thumb_id = get_post_thumbnail_id($p->ID);
    $thumb_url = wp_get_attachment_url($thumb_id);
    $thumb_file = basename($thumb_url);
    echo $p->post_date . " | ID: " . $p->ID . " | Thumb: " . $thumb_file . " | " . $p->post_title . PHP_EOL;
}
"""

remote_check_file = "temp_check_scheduled.php"
sftp = ssh.open_sftp()
with sftp.open(remote_check_file, "w") as f:
    f.write("<?php\n" + php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command(f"/usr/local/php/8.2/bin/php {remote_check_file} && rm {remote_check_file}")
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
