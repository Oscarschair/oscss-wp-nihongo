import paramiko
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

php_update = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$posts = get_posts(array(
    'post_type' => 'post',
    'post_status' => 'any',
    'numberposts' => -1
));

$updated_count = 0;

foreach ($posts as $p) {
    $content = $p->post_content;
    $new_content = str_replace('<rt>えみ</rt>', '<rt>わら</rt>', $content);
    $new_content = str_replace('（笑）', '（<ruby>笑<rt>わら</rt></ruby>）', $new_content);
    $new_content = str_replace('（<ruby>笑顔<rt>えがお</rt></ruby>のスタンプ）', '😊', $new_content);
    $new_content = str_replace('（笑顔のスタンプ）', '😊', $new_content);
    
    if ($new_content !== $content) {
        wp_update_post(array(
            'ID' => $p->ID,
            'post_content' => $new_content
        ));
        $updated_count++;
        echo "[UPDATED] Post ID: " . $p->ID . " - " . $p->post_title . PHP_EOL;
    }
}

echo "Total updated posts: " . $updated_count . PHP_EOL;

if (has_action('litespeed_purge_all')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache Purged All!" . PHP_EOL;
}
"""

sftp = ssh.open_sftp()
with sftp.open('replace_wara.php', 'w') as f:
    f.write(php_update)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php replace_wara.php && rm replace_wara.php')
out = stdout.read().decode('utf-8', errors='replace')
print(out)
ssh.close()
