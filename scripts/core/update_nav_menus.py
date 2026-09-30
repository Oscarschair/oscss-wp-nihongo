import paramiko
import json
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

$menu_id = 6; // グロナビメニュー
$items = wp_get_nav_menu_items($menu_id);

echo "CURRENT ITEMS:\\n";
$exists = false;
$max_order = 0;
foreach ($items as $it) {
    echo "- ID: {$it->ID}, Title: {$it->title}, URL: {$it->url}, Order: {$it->menu_order}, Parent: {$it->menu_item_parent}\\n";
    if (strpos($it->url, '/about') !== false || $it->title === '日本語学習帳について') {
        $exists = true;
    }
    if ($it->menu_order > $max_order) {
        $max_order = $it->menu_order;
    }
}

if (!$exists) {
    echo "\\nAdding '日本語学習帳について'...\\n";
    
    // 既存の項目順序を調整して、「記事一覧」の後、「オスカーのAIノートへ」の前に挿入、または末尾に追加
    // メニュー項目作成
    $item_id = wp_update_nav_menu_item($menu_id, 0, array(
        'menu-item-title'   => '日本語学習帳について',
        'menu-item-url'     => home_url('/about/'),
        'menu-item-status'  => 'publish',
        'menu-item-type'    => 'custom',
        'menu-item-position'=> 3, // 記事一覧の次
    ));
    
    echo "Added menu item ID: {$item_id}\\n";
} else {
    echo "\\nMenu item '日本語学習帳について' already exists.\\n";
}

if (defined('LSCWP_V')) {
    do_action('litespeed_purge_all');
}
if (function_exists('opcache_reset')) {
    @opcache_reset();
}
echo "SUCCESS\\n";
"""

remote_php = 'web/nihongo.oscarchair.jp/temp_update_menu.php'
with sftp.file(remote_php, 'w') as f:
    f.write(php_code)

stdin, stdout, stderr = ssh.exec_command(f'LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php $HOME/{remote_php} && rm -f $HOME/{remote_php}')
print(stdout.read().decode('utf-8', errors='ignore'))
sftp.close()
ssh.close()
