import os
import sys
import paramiko

# Load .env.deploy
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

# 1. Upload thumbnail images to remote theme/assets/images/thumbnails
local_thumbs_dir = r'c:\Users\user\git\oscss-wp-nihongo\assets\images\thumbnails'
remote_thumbs_dir = f'{deploy_dir.rstrip("/")}/assets/images/thumbnails'

try:
    sftp.mkdir(f'{deploy_dir.rstrip("/")}/assets/images')
except:
    pass
try:
    sftp.mkdir(remote_thumbs_dir)
except:
    pass

for f in os.listdir(local_thumbs_dir):
    local_file = os.path.join(local_thumbs_dir, f)
    remote_file = f'{remote_thumbs_dir}/{f}'
    print(f'Uploading {f}...')
    sftp.put(local_file, remote_file)

# 2. PHP script to register each thumbnail as featured image in WordPress
php_code = """<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');
require_once(ABSPATH . 'wp-admin/includes/file.php');
require_once(ABSPATH . 'wp-admin/includes/media.php');

$mapping = array(
    1  => 'thumb-post-1.jpg',
    36 => 'thumb-post-36.jpg',
    30 => 'thumb-post-30.jpg',
    19 => 'thumb-post-19.jpg',
    85 => 'thumb-post-85.jpg',
    44 => 'thumb-post-44.jpg',
);

$theme_dir = get_template_directory();

foreach ($mapping as $post_id => $filename) {
    $file_path = $theme_dir . '/assets/images/thumbnails/' . $filename;
    if (!file_exists($file_path)) {
        echo "File not found: {$file_path}\\n";
        continue;
    }
    
    // Copy to uploads
    $upload_dir = wp_upload_dir();
    $dest_filename = wp_unique_filename($upload_dir['path'], $filename);
    $dest_path = $upload_dir['path'] . '/' . $dest_filename;
    copy($file_path, $dest_path);
    
    $filetype = wp_check_filetype($dest_filename, null);
    
    $attachment = array(
        'guid'           => $upload_dir['url'] . '/' . $dest_filename,
        'post_mime_type' => $filetype['type'],
        'post_title'     => preg_replace('/\\.[^.]+$/', '', $dest_filename),
        'post_content'   => '',
        'post_status'    => 'inherit'
    );
    
    $attach_id = wp_insert_attachment($attachment, $dest_path, $post_id);
    $attach_data = wp_generate_attachment_metadata($attach_id, $dest_path);
    wp_update_attachment_metadata($attach_id, $attach_data);
    
    set_post_thumbnail($post_id, $attach_id);
    echo "Post {$post_id} featured image updated to attachment ID: {$attach_id}\\n";
}

// Flush cache
if (function_exists('opcache_reset')) {
    opcache_reset();
}
do_action('litespeed_purge_all');
if (class_exists('LiteSpeed\\Purge')) {
    LiteSpeed\\Purge::purge_all();
}
echo "Cache flushed\\n";
"""

with sftp.file(f'{deploy_dir.rstrip("/")}/set_featured_images.php', 'w') as f:
    f.write(php_code)
sftp.close()

print('Running remote featured image setup...')
stdin, stdout, stderr = ssh.exec_command(f'/usr/local/php/8.2/bin/php {deploy_dir.rstrip("/")}/set_featured_images.php')
out = stdout.read().decode('utf-8', errors='ignore')
err = stderr.read().decode('utf-8', errors='ignore')

print("Output:")
print(out)
if err.strip():
    print("Stderr:", err)

ssh.exec_command(f'rm -f {deploy_dir.rstrip("/")}/set_featured_images.php')
ssh.close()
print('Finished setting featured images!')
