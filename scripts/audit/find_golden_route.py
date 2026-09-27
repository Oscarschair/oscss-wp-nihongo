import paramiko
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

php_code = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$posts = get_posts(array(
    'post_type' => 'post',
    'post_status' => 'any',
    'numberposts' => -1
));

foreach ($posts as $p) {
    if (strpos($p->post_content, '黄金攻略ルート') !== false || strpos($p->post_content, '1F 総合案内') !== false || strpos($p->post_content, '市役所ダンジョン') !== false) {
        echo "Found in Post ID: " . $p->ID . " - " . $p->post_title . PHP_EOL;
        $pos = strpos($p->post_content, '黄金攻略ルート');
        if ($pos !== false) {
            echo substr($p->post_content, $pos - 100, 1000) . PHP_EOL;
        } else {
            $pos2 = strpos($p->post_content, '1F');
            if ($pos2 !== false) echo substr($p->post_content, $pos2 - 100, 1000) . PHP_EOL;
        }
    }
}
"""

sftp = ssh.open_sftp()
with sftp.open('find_route.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php find_route.php && rm find_route.php')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
