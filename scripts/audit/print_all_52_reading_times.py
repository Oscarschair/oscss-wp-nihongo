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

echo "=== 全52記事 読了目安時間・ステータス完全監査 ===\\n";
$dist = [];
foreach ($rows as $i => $r) {
    $p = get_post($r->ID);
    $time = oscss_get_reading_time($p);
    $dist[$time] = ($dist[$time] ?? 0) + 1;
    $idx = $i + 1;
    echo sprintf("[%02d] ID:%-4d | %s | %-7s | 約%2d分 | %s\\n", $idx, $r->ID, $r->post_date, $r->post_status, $time, mb_substr($r->post_title, 0, 35));
}

echo "\\n=== 読了目安時間の分布 ===\\n";
ksort($dist);
foreach ($dist as $mins => $cnt) {
    echo "約{$mins}分: {$cnt}記事\\n";
}
"""

sftp = ssh.open_sftp()
with sftp.open('print_all.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php print_all.php && rm print_all.php')
out = stdout.read().decode('utf-8', errors='replace')
print(out)
ssh.close()
