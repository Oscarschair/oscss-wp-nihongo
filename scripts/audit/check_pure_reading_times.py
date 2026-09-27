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
$rows = $wpdb->get_results("SELECT ID, post_date, post_status, post_title, post_name FROM {$wpdb->posts} WHERE post_type='post' AND post_status IN ('publish','future') ORDER BY post_date ASC");

echo "Total posts: " . count($rows) . "\\n";
$under_7 = [];
foreach ($rows as $r) {
    $p = get_post($r->ID);
    $time = oscss_get_reading_time($p);
    
    // Calculate pure text length
    $content = strip_shortcodes($p->post_content);
    $content = preg_replace('/<rt>.*?<\/rt>/su', '', $content);
    $content = wp_strip_all_tags($content);
    $content = preg_replace('/\\s+/', '', $content);
    $char_count = mb_strlen($content, 'UTF-8');
    
    if ($time < 7) {
        $under_7[] = [$r->ID, $r->post_date, $time, $char_count, $r->post_title];
    }
}

echo "Posts with reading time < 7 mins: " . count($under_7) . "\\n";
foreach ($under_7 as $item) {
    echo "ID {$item[0]} | {$item[1]} | 約{$item[2]}分 ({$item[3]}字) | " . mb_substr($item[4], 0, 35) . "\\n";
}
"""

sftp = ssh.open_sftp()
with sftp.open('check_pure_reading_times.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php check_pure_reading_times.php && rm check_pure_reading_times.php')
out = stdout.read().decode('utf-8', errors='replace')
print(out)
ssh.close()
