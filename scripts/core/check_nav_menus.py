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
$locations = get_nav_menu_locations();
$menus = wp_get_nav_menus();
$menu_data = array();
foreach ($menus as $m) {
    $items = wp_get_nav_menu_items($m->term_id);
    $item_titles = array();
    if ($items) {
        foreach ($items as $it) {
            $item_titles[] = $it->title . ' (' . $it->url . ')';
        }
    }
    $menu_data[] = array(
        'term_id' => $m->term_id,
        'name' => $m->name,
        'slug' => $m->slug,
        'items' => $item_titles
    );
}
echo json_encode(array('locations' => $locations, 'menus' => $menu_data), JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
"""
remote_php = 'web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/temp_menu_check.php'
with sftp.file(remote_php, 'w') as f:
    f.write(php_code)
stdin, stdout, stderr = ssh.exec_command('LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php $HOME/' + remote_php + ' && rm -f $HOME/' + remote_php)
print(stdout.read().decode('utf-8', errors='ignore'))
sftp.close()
ssh.close()
