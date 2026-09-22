import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

php_sync = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');

$theme_dir = getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/';
$upload_dir = wp_upload_dir();

$attachments = get_posts(array(
    'post_type' => 'attachment',
    'numberposts' => -1,
    'post_status' => 'any'
));

$updated_count = 0;
foreach ($attachments as $att) {
    $file_path = get_attached_file($att->ID);
    $base = basename($file_path);
    
    $thumb_candidate = $theme_dir . 'assets/images/thumbnails/' . $base;
    $post_candidate = $theme_dir . 'assets/images/posts/' . $base;
    
    $source = '';
    if (file_exists($thumb_candidate)) {
        $source = $thumb_candidate;
    } elseif (file_exists($post_candidate)) {
        $source = $post_candidate;
    }
    
    if ($source) {
        copy($source, $file_path);
        $attach_data = wp_generate_attachment_metadata($att->ID, $file_path);
        wp_update_attachment_metadata($att->ID, $attach_data);
        echo "Updated attachment ID {$att->ID}: {$base}\n";
        $updated_count++;
    }
}

if (function_exists('opcache_reset')) { opcache_reset(); }
if (class_exists('LiteSpeed\\Purge')) { LiteSpeed\\Purge::purge_all(); }
echo "Finished updating {$updated_count} attachments in uploads directory!\n";
?>"""

with sftp.open('sync_uploads.php', 'w') as f:
    f.write(php_sync)

print('Running sync_uploads.php on remote server...')
stdin, stdout, stderr = ssh.exec_command('LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php sync_uploads.php && rm sync_uploads.php')
out = stdout.read().decode('utf-8')
print(out)
err = stderr.read().decode('utf-8')
if err:
    print('ERR:', err)

sftp.close()
ssh.close()
