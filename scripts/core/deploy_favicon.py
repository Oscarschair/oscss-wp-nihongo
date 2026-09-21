import os
import paramiko

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

# 1. テーマ内の assets/images にファビコン一式を配置
remote_theme_img = 'web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images'
files = [
    'favicon-512x512.png',
    'favicon-192x192.png',
    'apple-touch-icon.png',
    'favicon-32x32.png',
    'favicon-16x16.png',
    'favicon.ico'
]

for f in files:
    local_p = f'assets/images/{f}'
    remote_p = f'{remote_theme_img}/{f}'
    sftp.put(local_p, remote_p)
    print(f'Uploaded to theme: {remote_p}')

# 2. サイト直下 (web/nihongo.oscarchair.jp/favicon.ico) にも配置
sftp.put('assets/images/favicon.ico', 'web/nihongo.oscarchair.jp/favicon.ico')
print('Uploaded to web root: favicon.ico')

# 3. WordPressのメディアライブラリに 512x512 を登録し、site_icon オプションに設定
php_script = r'''<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$upload_dir = wp_upload_dir();
$filename = 'site-icon-gakushucho-512x512.png';
$dest_file = $upload_dir['path'] . '/' . $filename;
$src_file = getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/favicon-512x512.png';

copy($src_file, $dest_file);

$filetype = wp_check_filetype($filename, null);
$attachment = array(
    'guid'           => $upload_dir['url'] . '/' . $filename, 
    'post_mime_type' => $filetype['type'],
    'post_title'     => 'オスカーの日本語学習帳 サイトアイコン (学習ノート＆桜色しおり)',
    'post_content'   => '',
    'post_status'    => 'inherit'
);

require_once(ABSPATH . 'wp-admin/includes/image.php');
$attach_id = wp_insert_attachment($attachment, $dest_file);
$attach_data = wp_generate_attachment_metadata($attach_id, $dest_file);
wp_update_attachment_metadata($attach_id, $attach_data);

// WordPressのサイトアイコンに設定
update_option('site_icon', $attach_id);
echo "Successfully set WordPress site_icon to Attachment ID: {$attach_id}\n";

// キャッシュパージ
if (function_exists('opcache_reset')) { opcache_reset(); }
if (class_exists('LiteSpeed\Purge')) { 
    \LiteSpeed\Purge::purge_all(); 
}
do_action('litespeed_purge_all');
wp_cache_flush();

echo "Caches purged!\n";
?>'''

with sftp.open('set_site_icon.php', 'w') as f:
    f.write(php_script)

stdin, stdout, stderr = ssh.exec_command('LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php set_site_icon.php && rm set_site_icon.php')
out = stdout.read().decode('utf-8', errors='ignore')
print("OUTPUT:\n", out)

sftp.close()
ssh.close()
print("Favicon deployment finished.")
