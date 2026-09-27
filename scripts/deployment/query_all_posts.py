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
ini_set('display_errors', 1);
error_reporting(E_ALL);
echo "PHP START\\n";
$wp_load = getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php';
echo "Path: " . $wp_load . "\\n";
if (file_exists($wp_load)) {
    echo "Exists!\\n";
    require_once $wp_load;
    echo "Loaded WP!\\n";
    global $wpdb;
    $rows = $wpdb->get_results("SELECT ID, post_date, post_status, post_name, post_title FROM {$wpdb->posts} WHERE post_type='post' AND post_status IN ('publish','future','draft') ORDER BY post_date ASC");
    echo "Count: " . count($rows) . "\\n";
    foreach ($rows as $r) {
        echo $r->ID . " | " . $r->post_status . " | " . $r->post_date . " | " . $r->post_name . " | " . $r->post_title . "\\n";
    }
} else {
    echo "Not found!\\n";
}
"""

sftp = ssh.open_sftp()
with sftp.open('query_all_posts.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php query_all_posts.php && rm query_all_posts.php')
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')
print("STDOUT:\n", out)
if err:
    print("STDERR:\n", err)
ssh.close()
