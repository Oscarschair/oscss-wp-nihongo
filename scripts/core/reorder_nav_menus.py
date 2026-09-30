import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

env_data = {}
with open('.env.deploy', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env_data[k.strip()] = v.strip()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    hostname=env_data['SSH_HOST'],
    port=int(env_data['SSH_PORT']),
    username=env_data['SSH_USER'],
    password=env_data['SSH_PASS'],
    look_for_keys=False,
    allow_agent=False
)
sftp = ssh.open_sftp()

php_code = """<?php
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$menu_id = 6;
$items = wp_get_nav_menu_items($menu_id);

// 順番を整理
// 1. HOME (ID: 52)
// 2. 記事一覧 (ID: 2076)
// 3. 日本語学習帳について (ID: 3100)
// 4. カテゴリ (ID: 69)
// 5. カルチャーショック (ID: 70, parent: 69)
// 6. くらべてみました (ID: 71, parent: 69)
// 7. ことばのあや (ID: 72, parent: 69)
// 8. 街角サバイバル (ID: 193, parent: 69)
// 9. オスカーのAIノートへ (ID: 64)

$order_map = array(
    52 => 1,
    2076 => 2,
    3100 => 3,
    69 => 4,
    70 => 5,
    71 => 6,
    72 => 7,
    193 => 8,
    64 => 9,
);

foreach ($order_map as $post_id => $order) {
    wp_update_post(array(
        'ID' => $post_id,
        'menu_order' => $order
    ));
}

echo "UPDATED MENU ORDERS:\\n";
$new_items = wp_get_nav_menu_items($menu_id);
foreach ($new_items as $it) {
    echo "- Order: {$it->menu_order}, Title: {$it->title}, URL: {$it->url}, Parent: {$it->menu_item_parent}\\n";
}

if (defined('LSCWP_V')) {
    do_action('litespeed_purge_all');
}
if (function_exists('opcache_reset')) {
    @opcache_reset();
}
echo "SUCCESS\\n";
"""

remote_php = 'web/nihongo.oscarchair.jp/temp_reorder_menu.php'
with sftp.file(remote_php, 'w') as f:
    f.write(php_code)

stdin, stdout, stderr = ssh.exec_command(f'LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php $HOME/{remote_php} && rm -f $HOME/{remote_php}')
print(stdout.read().decode('utf-8', errors='ignore'))
sftp.close()
ssh.close()
