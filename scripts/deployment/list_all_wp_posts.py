import sys
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

php_code = """<?php
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
global $wpdb;
$rows = $wpdb->get_results("SELECT ID, post_date, post_status, post_name, post_title FROM {$wpdb->posts} WHERE post_type='post' AND post_status IN ('publish','future','draft') ORDER BY post_date ASC");
foreach ($rows as $r) {
    $p = get_post($r->ID);
    $read_time = function_exists('oscss_get_reading_time') ? oscss_get_reading_time($p) : 0;
    echo $r->ID . "\\t" . $r->post_date . "\\t" . $r->post_status . "\\t約" . $read_time . "分\\t" . $r->post_name . "\\t" . $r->post_title . "\\n";
}
"""

sftp = ssh.open_sftp()
with sftp.open('list_all_wp_posts.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php list_all_wp_posts.php && rm list_all_wp_posts.php')
out = stdout.read().decode('utf-8', errors='replace')
with open('all_wp_posts.tsv', 'w', encoding='utf-8') as f:
    f.write(out)

print("Saved all WordPress posts to all_wp_posts.tsv")
ssh.close()
