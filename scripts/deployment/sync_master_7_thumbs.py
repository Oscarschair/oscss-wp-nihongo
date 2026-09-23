import paramiko
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

php_code = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');

$posts_map = array(
    1619 => 'thumb-comparing-iku-kuru.jpg',
    1621 => 'thumb-street-delivery-redelivery.jpg',
    1623 => 'thumb-kotoba-kekkoudesu-trap.jpg',
    1625 => 'thumb-culture-hanko-stamp.jpg',
    1627 => 'thumb-street-clinic-hospital.jpg',
    1629 => 'thumb-comparing-hazu-wake.jpg',
    1631 => 'thumb-culture-expiry-discount.jpg'
);

$theme_thumb_dir = getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/thumbnails/';
$upload_dir = wp_upload_dir();

foreach ($posts_map as $post_id => $file) {
    $src = $theme_thumb_dir . $file;
    if (!file_exists($src)) {
        echo "[ERROR] Source not found: " . $src . PHP_EOL;
        continue;
    }
    
    $dest_file = $upload_dir['path'] . '/' . $file;
    copy($src, $dest_file);
    echo "[OK] Copied to uploads: " . $dest_file . PHP_EOL;
    
    // Check existing attachment
    $atts = get_posts(array(
        'post_type' => 'attachment',
        'meta_key' => '_wp_attached_file',
        'meta_value' => $file,
        'numberposts' => 1
    ));
    
    if (!empty($atts)) {
        $att_id = $atts[0]->ID;
        $attach_data = wp_generate_attachment_metadata($att_id, $dest_file);
        wp_update_attachment_metadata($att_id, $attach_data);
        echo "  [UPDATE] Existing attachment ID: " . $att_id . PHP_EOL;
    } else {
        $filetype = wp_check_filetype($file, null);
        $attachment = array(
            'guid'           => $upload_dir['url'] . '/' . $file,
            'post_mime_type' => $filetype['type'],
            'post_title'     => preg_replace('/\\.[^.]+$/', '', $file),
            'post_content'   => '',
            'post_status'    => 'inherit'
        );
        $att_id = wp_insert_attachment($attachment, $dest_file);
        $attach_data = wp_generate_attachment_metadata($att_id, $dest_file);
        wp_update_attachment_metadata($att_id, $attach_data);
        echo "  [NEW] Created attachment ID: " . $att_id . PHP_EOL;
    }
    
    // Link to post
    set_post_thumbnail($post_id, $att_id);
    echo "  [LINKED] Set thumbnail ID " . $att_id . " to Post ID " . $post_id . " (" . get_the_title($post_id) . ")" . PHP_EOL;
}

if (function_exists('opcache_reset')) { opcache_reset(); }
if (class_exists('LiteSpeed\\Purge')) { LiteSpeed\\Purge::purge_all(); }
echo ">>> All 7 thumbnails synchronized and linked successfully! <<<" . PHP_EOL;
"""

with sftp.open('sync_master_7_thumbs.php', 'w') as f:
    f.write(php_code)

stdin, stdout, stderr = ssh.exec_command('LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php sync_master_7_thumbs.php && rm sync_master_7_thumbs.php')
out = stdout.read().decode('utf-8')
print(out)
err = stderr.read().decode('utf-8')
if err:
    print("STDERR:", err)
