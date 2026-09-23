import paramiko
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

php_code = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
$posts = get_posts(array('post_type' => 'post', 'numberposts' => -1, 'post_status' => array('publish', 'future', 'draft')));
foreach ($posts as $p) {
    $cats = wp_get_post_categories($p->ID, array('fields' => 'names'));
    $cat_str = implode(', ', $cats);
    echo $p->ID . ' | ' . $p->post_status . ' | ' . $cat_str . ' | ' . $p->post_title . PHP_EOL;
}
"""

with sftp.open('check_titles.php', 'w') as f:
    f.write(php_code)

stdin, stdout, stderr = ssh.exec_command('LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php check_titles.php && rm check_titles.php')
out = stdout.read().decode('utf-8')
print(out)
