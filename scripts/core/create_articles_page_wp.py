import paramiko
import json

env_data = {}
with open('.env.deploy', 'r', encoding='utf-8') as ef:
    for line in ef:
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

// 1. 固定ページ 'articles' の確認・作成
$page_slug = 'articles';
$page_title = '学習ノート一覧';
$existing_page = get_page_by_path($page_slug);

if (!$existing_page) {
    $page_id = wp_insert_post(array(
        'post_title'     => $page_title,
        'post_name'      => $page_slug,
        'post_status'    => 'publish',
        'post_type'      => 'page',
        'comment_status' => 'closed',
        'ping_status'    => 'closed',
    ));
    update_post_meta($page_id, '_wp_page_template', 'page-articles.php');
    $status_msg = "Created page ID: $page_id";
} else {
    $page_id = $existing_page->ID;
    update_post_meta($page_id, '_wp_page_template', 'page-articles.php');
    $status_msg = "Existing page ID: $page_id updated template to page-articles.php";
}

// 2. ナビゲーションメニュー（term_id: 6）に記事一覧を追加
$menu_id = 6;
$menu_items = wp_get_nav_menu_items($menu_id);
$has_articles_link = false;
$home_item_menu_order = 1;

if ($menu_items) {
    foreach ($menu_items as $item) {
        if (strpos($item->url, '/articles') !== false || $item->title === '記事一覧' || $item->title === '学習ノート一覧') {
            $has_articles_link = true;
            break;
        }
    }
}

if (!$has_articles_link) {
    // HOMEの次（menu_order 2）に挿入するため、既存項目のmenu_orderをシフト
    if ($menu_items) {
        foreach ($menu_items as $item) {
            if ($item->menu_order >= 2) {
                wp_update_post(array(
                    'ID'         => $item->ID,
                    'menu_order' => $item->menu_order + 1,
                ));
            }
        }
    }

    $item_id = wp_update_nav_menu_item($menu_id, 0, array(
        'menu-item-title'   => '記事一覧',
        'menu-item-url'     => home_url('/articles/'),
        'menu-item-status'  => 'publish',
        'menu-item-type'    => 'custom',
        'menu-item-position'=> 2,
    ));
    $menu_msg = "Added '記事一覧' to menu (item ID: $item_id)";
} else {
    $menu_msg = "'記事一覧' already exists in menu";
}

// パーマリンクをフラッシュ
flush_rewrite_rules();

echo json_encode(array(
    'page_status' => $status_msg,
    'page_id'     => $page_id,
    'page_url'    => get_permalink($page_id),
    'menu_status' => $menu_msg,
), JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
"""

remote_php = 'web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/temp_create_articles_page.php'
with sftp.file(remote_php, 'w') as f:
    f.write(php_code)

stdin, stdout, stderr = ssh.exec_command('LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php $HOME/' + remote_php + ' && rm -f $HOME/' + remote_php)
out = stdout.read().decode('utf-8', errors='ignore')
print(out)

sftp.close()
ssh.close()
