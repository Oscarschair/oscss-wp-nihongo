import paramiko
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

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

# 1. ローカルの更新画像をテーマの assets/images/thumbnails/ にアップロード
local_thumb = 'assets/images/thumbnails/thumb-street-kaitenzushi-rpg.jpg'
remote_theme_thumb = 'web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/thumbnails/thumb-street-kaitenzushi-rpg.jpg'

sftp.put(local_thumb, remote_theme_thumb)
print(f"Uploaded {local_thumb} -> {remote_theme_thumb}")

# 2. WordPress側の添付ファイル（uploads/）を上書き更新し、リサイズ画像を再生成
php_code = """<?php
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');

$slug = 'street-japanese-kaitenzushi-hot-water-express-lane-survival-guide';
$post = get_page_by_path($slug, OBJECT, 'post');

if (!$post) {
    echo "Post not found for slug: $slug\n";
    exit;
}

$thumb_filename = 'thumb-street-kaitenzushi-rpg.jpg';
$theme_thumb_path = get_stylesheet_directory() . '/assets/images/thumbnails/' . $thumb_filename;

// 既存のアイキャッチIDを取得
$current_thumb_id = get_post_thumbnail_id($post->ID);

if ($current_thumb_id) {
    $attached_file = get_attached_file($current_thumb_id);
    if ($attached_file && file_exists($theme_thumb_path)) {
        // 元ファイルを新しいテーマ画像で上書き
        copy($theme_thumb_path, $attached_file);
        // 各種サムネイルサイズを再生成
        $attach_data = wp_generate_attachment_metadata($current_thumb_id, $attached_file);
        wp_update_attachment_metadata($current_thumb_id, $attach_data);
        echo "Updated existing attachment ID: $current_thumb_id and regenerated metadata.\n";
    }
} else {
    // 新規アタッチメントとして登録
    $upload_dir = wp_upload_dir();
    $dest_file = $upload_dir['path'] . '/' . $thumb_filename;
    copy($theme_thumb_path, $dest_file);
    $filetype = wp_check_filetype($thumb_filename, null);
    $attachment = array(
        'guid'           => $upload_dir['url'] . '/' . $thumb_filename,
        'post_mime_type' => $filetype['type'],
        'post_title'     => preg_replace('/\.[^.]+$/', '', $thumb_filename),
        'post_content'   => '',
        'post_status'    => 'inherit'
    );
    $new_thumb_id = wp_insert_attachment($attachment, $dest_file, $post->ID);
    $attach_data = wp_generate_attachment_metadata($new_thumb_id, $dest_file);
    wp_update_attachment_metadata($new_thumb_id, $attach_data);
    set_post_thumbnail($post->ID, $new_thumb_id);
    echo "Created new attachment ID: $new_thumb_id and set as thumbnail.\n";
}

clean_post_cache($post->ID);

// キャッシュパージ
if (function_exists('litespeed_purge_all')) {
    litespeed_purge_all();
}
if (function_exists('opcache_reset')) {
    opcache_reset();
}
echo "Finished updating thumbnail for {$post->post_title}\n";
"""

remote_php = 'web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/temp_update_thumb.php'
with sftp.file(remote_php, 'w') as f:
    f.write(php_code)

stdin, stdout, stderr = ssh.exec_command('LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php $HOME/' + remote_php + ' && rm -f $HOME/' + remote_php)
out = stdout.read().decode('utf-8', errors='ignore')
print(out)

sftp.close()
ssh.close()
