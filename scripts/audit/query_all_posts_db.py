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
global $wpdb;
$rows = $wpdb->get_results("SELECT ID, post_title, post_status, post_date FROM {$wpdb->posts} WHERE post_type = 'post' ORDER BY post_date DESC");
foreach ($rows as $r) {
    $cats = wp_get_post_categories($r->ID, array('fields' => 'names'));
    $cat_str = implode(', ', $cats);
    echo $r->ID . ' | ' . $r->post_status . ' | ' . $r->post_date . ' | ' . $cat_str . ' | ' . $r->post_title . PHP_EOL;
}
"""

with sftp.open('query_posts.php', 'w') as f:
    f.write(php_code)

stdin, stdout, stderr = ssh.exec_command('LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php query_posts.php && rm query_posts.php')
out = stdout.read().decode('utf-8')
print(out)
