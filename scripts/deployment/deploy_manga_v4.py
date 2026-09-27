import shutil
import sys
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

src = r"C:\Users\user\.gemini\antigravity-ide\brain\c8ff313e-4ec8-47e9-b866-72ee31d60fa5\manga_01_daijoubu_v4_1790550823060.jpg"
dst = "assets/images/posts/manga-01-daijoubu-trap.jpg"
shutil.copy2(src, dst)
print("Copied to local:", dst)

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

remote_theme_img = "web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/posts/manga-01-daijoubu-trap.jpg"
sftp.put(dst, remote_theme_img)
print("Uploaded to remote theme:", remote_theme_img)

php_code = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');
require_once(ABSPATH . 'wp-admin/includes/file.php');
require_once(ABSPATH . 'wp-admin/includes/media.php');

$post_id = 2721;
$upload_dir = wp_upload_dir();
$img_source = get_stylesheet_directory() . '/assets/images/posts/manga-01-daijoubu-trap.jpg';

$existing_thumb_id = get_post_thumbnail_id($post_id);
if ($existing_thumb_id) {
    wp_delete_attachment($existing_thumb_id, true);
}

$filename = 'manga-01-daijoubu-trap-' . time() . '.jpg';
$upload_path = $upload_dir['path'] . '/' . $filename;
copy($img_source, $upload_path);

$filetype = wp_check_filetype($filename, null);
$attachment = array(
    'guid'           => $upload_dir['url'] . '/' . $filename, 
    'post_mime_type' => $filetype['type'],
    'post_title'     => 'manga-01-daijoubu-trap',
    'post_content'   => '',
    'post_status'    => 'inherit'
);

$attach_id = wp_insert_attachment($attachment, $upload_path, $post_id);
$attach_data = wp_generate_attachment_metadata($attach_id, $upload_path);
wp_update_attachment_metadata($attach_id, $attach_data);
set_post_thumbnail($post_id, $attach_id);

echo "Thumbnail successfully updated to attach ID: {$attach_id}\\n";

if (has_action('litespeed_purge_all')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed cache purged!\\n";
}
"""

with sftp.open('update_thumb_v4.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php update_thumb_v4.php && rm update_thumb_v4.php')
out = stdout.read().decode('utf-8', errors='replace')
print("PHP OUTPUT:\n", out)
err = stderr.read().decode('utf-8', errors='replace')
if err:
    print("PHP STDERR:\n", err)

ssh.close()
print("All updated successfully!")
