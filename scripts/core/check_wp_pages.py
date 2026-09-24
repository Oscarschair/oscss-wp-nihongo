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
$show_on_front = get_option('show_on_front');
$page_on_front = get_option('page_on_front');
$page_for_posts = get_option('page_for_posts');

$pages = get_pages();
$page_list = array();
foreach ($pages as $p) {
    $page_list[] = array('id' => $p->ID, 'title' => $p->post_title, 'slug' => $p->post_name);
}

echo json_encode(array(
    'show_on_front' => $show_on_front,
    'page_on_front' => $page_on_front,
    'page_for_posts' => $page_for_posts,
    'pages' => $page_list
), JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
"""

theme_dir = "web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo"
remote_php = f"{theme_dir}/check_wp_pages.php"

with sftp.file(remote_php, 'w') as f:
    f.write(php_code)

stdin, stdout, stderr = ssh.exec_command(f'LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php $HOME/{remote_php} && rm -f $HOME/{remote_php}')
out = stdout.read().decode('utf-8', errors='ignore')
sftp.close()
ssh.close()
print(out)
