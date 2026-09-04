import shutil
import paramiko

# 1. ローカル画像を上書きコピー
src_ice = r'C:\Users\user\.gemini\antigravity-ide\brain\4d088df4-e87c-4c0f-ae49-5ce9644d7e28\thumb_ice_water_pose_v3_1788529947752.jpg'
dest_ice = r'c:\Users\user\git\oscss-wp-nihongo\assets\images\thumbnails\thumb-culture-ice-water.jpg'
shutil.copyfile(src_ice, dest_ice)

src_train = r'C:\Users\user\.gemini\antigravity-ide\brain\4d088df4-e87c-4c0f-ae49-5ce9644d7e28\thumb_train_sleep_pose_var_1788529984492.jpg'
dest_train = r'c:\Users\user\git\oscss-wp-nihongo\assets\images\thumbnails\thumb-culture-train-sleep.jpg'
shutil.copyfile(src_train, dest_train)

print("Local thumbnails updated with varied shock poses!")

# 2. 本番サーバーへアップロード & WordPressアイキャッチ更新
env_data = {}
with open('.env.deploy', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env_data[k.strip()] = v.strip()

host = env_data.get('SSH_HOST', 'ssh.lolipop.jp')
port = int(env_data.get('SSH_PORT', 2222))
user = env_data.get('SSH_USER')
password = env_data.get('SSH_PASS')
deploy_dir = env_data.get('DEPLOY_DIR', '~/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/').replace('~/', '')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=host, port=port, username=user, password=password, look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

remote_thumbs_dir = f'{deploy_dir.rstrip("/")}/assets/images/thumbnails'
sftp.put(dest_ice, f'{remote_thumbs_dir}/thumb-culture-ice-water.jpg')
sftp.put(dest_train, f'{remote_thumbs_dir}/thumb-culture-train-sleep.jpg')
print("Uploaded varied thumbnails to server!")

remote_php = """<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');
require_once(ABSPATH . 'wp-admin/includes/file.php');
require_once(ABSPATH . 'wp-admin/includes/media.php');

$theme_dir = get_template_directory();

$mapping = array(
    109 => 'thumb-culture-ice-water.jpg',
    111 => 'thumb-culture-train-sleep.jpg'
);

foreach ($mapping as $post_id => $file) {
    $thumb_path = $theme_dir . '/assets/images/thumbnails/' . $file;
    if (file_exists($thumb_path)) {
        $wp_upload_dir = wp_upload_dir();
        $unique_filename = wp_unique_filename($wp_upload_dir['path'], 'v3-' . $file);
        $upload_file = $wp_upload_dir['path'] . '/' . $unique_filename;
        copy($thumb_path, $upload_file);
        
        $filetype = wp_check_filetype($unique_filename, null);
        $attachment = array(
            'post_mime_type' => $filetype['type'],
            'post_title'     => sanitize_file_name($unique_filename),
            'post_content'   => '',
            'post_status'    => 'inherit'
        );
        $attach_id = wp_insert_attachment($attachment, $upload_file, $post_id);
        $attach_data = wp_generate_attachment_metadata($attach_id, $upload_file);
        wp_update_attachment_metadata($attach_id, $attach_data);
        
        set_post_thumbnail($post_id, $attach_id);
        echo "Updated post $post_id thumbnail to attachment $attach_id\\n";
    }
}

if (defined('LSCWP_V')) {
    do_action('litespeed_purge_all');
}
if (class_exists('LiteSpeed\\Purge')) {
    LiteSpeed\\Purge::purge_all();
}
if (function_exists('opcache_reset')) {
    opcache_reset();
}
echo "Purged all cache!\\n";
"""

with sftp.open('update_thumb_tmp.php', 'w') as f:
    f.write(remote_php)

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php update_thumb_tmp.php')
out = stdout.read().decode('utf-8', errors='ignore')
print(out)

ssh.exec_command('rm update_thumb_tmp.php')
sftp.close()
ssh.close()
print("Complete!")
