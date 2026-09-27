import paramiko

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

php_check = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$post_ids = array(2472, 2474, 2476);
foreach ($post_ids as $pid) {
    $p = get_post($pid);
    $time = oscss_get_reading_time($p);
    
    $content = strip_shortcodes( $p->post_content );
    $content = preg_replace( '/<rt>.*?<\\/rt>/su', '', $content );
    $content = wp_strip_all_tags( $content );
    $content = preg_replace( '/\\s+/', '', $content );
    $chars = mb_strlen( $content, 'UTF-8' );
    
    echo "Post ID {$pid}: {$chars} chars -> 読了目安: 約{$time}分\\n";
}
"""

sftp = ssh.open_sftp()
with sftp.open('check_times.php', 'w') as f:
    f.write(php_check)

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php check_times.php && rm check_times.php')
print(stdout.read().decode('utf-8', errors='replace'))

sftp.close()
ssh.close()
