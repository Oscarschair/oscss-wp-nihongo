import paramiko

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

php_code = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');

$post_id = 3156;
$thumb_file = 'thumb-culture-weekend-school-uniform.jpg';
$theme_thumb_dir = getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/thumbnails/';
$upload_dir = wp_upload_dir();

$src = $theme_thumb_dir . $thumb_file;
$dest_file = $upload_dir['path'] . '/' . $thumb_file;

if (copy($src, $dest_file)) {
    echo "Copied successfully to uploads!" . PHP_EOL;
    $filetype = wp_check_filetype($thumb_file, null);
    $attachment = array(
        'guid'           => $upload_dir['url'] . '/' . $thumb_file,
        'post_mime_type' => $filetype['type'],
        'post_title'     => preg_replace('/\\.[^.]+$/', '', $thumb_file),
        'post_content'   => '',
        'post_status'    => 'inherit'
    );
    $att_id = wp_insert_attachment($attachment, $dest_file, $post_id);
    $attach_data = wp_generate_attachment_metadata($att_id, $dest_file);
    wp_update_attachment_metadata($att_id, $attach_data);
    set_post_thumbnail($post_id, $att_id);
    echo "Set thumbnail for post 3156 successfully! Att ID: " . $att_id . PHP_EOL;
} else {
    echo "Copy failed!" . PHP_EOL;
}
"""

with sftp.open('fix_thumb_3156.php', 'w') as f:
    f.write(php_code)

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php fix_thumb_3156.php && rm fix_thumb_3156.php')
print(stdout.read().decode('utf-8', errors='replace'))
print('STDERR:', stderr.read().decode('utf-8', errors='replace'))
sftp.close()
ssh.close()
