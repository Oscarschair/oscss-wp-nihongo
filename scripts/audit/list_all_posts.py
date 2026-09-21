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

php_code = r"""<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$args = array(
    'post_type' => 'post',
    'post_status' => array('publish', 'future'),
    'posts_per_page' => -1,
    'orderby' => 'date',
    'order' => 'ASC'
);
$posts = get_posts($args);

foreach ($posts as $post) {
    $thumb_id = get_post_thumbnail_id($post->ID);
    $file = get_attached_file($thumb_id);
    $cats = wp_get_post_categories($post->ID, ['fields' => 'slugs']);
    $cat_slug = !empty($cats) ? $cats[0] : 'none';
    echo "ID: " . $post->ID . " | DATE: " . $post->post_date . " | CAT: " . $cat_slug . " | THUMB: " . basename($file) . " | SLUG: " . $post->post_name . "\n";
}
"""

sftp = ssh.open_sftp()
with sftp.open('list_all_posts.php', 'w') as f:
    f.write(php_code)

stdin, stdout, stderr = ssh.exec_command('LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php list_all_posts.php && rm list_all_posts.php')
print(stdout.read().decode('utf-8'))
ssh.close()
