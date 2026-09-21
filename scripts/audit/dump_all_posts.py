import paramiko
import json
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

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
sftp = ssh.open_sftp()

php_code = """<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$posts = get_posts(array(
    'post_type' => 'post',
    'numberposts' => -1,
    'post_status' => array('publish', 'future'),
    'orderby' => 'date',
    'order' => 'ASC'
));

$res = array();
foreach ($posts as $p) {
    $cats = wp_get_post_categories($p->ID, array('fields' => 'names'));
    $cat_slugs = array();
    foreach (wp_get_post_categories($p->ID) as $c_id) {
        $c = get_category($c_id);
        if ($c) $cat_slugs[] = $c->slug;
    }
    $res[] = array(
        'id' => $p->ID,
        'date' => $p->post_date,
        'status' => $p->post_status,
        'slug' => $p->post_name,
        'title' => $p->post_title,
        'cat_names' => $cats,
        'cat_slugs' => $cat_slugs,
        'url' => get_permalink($p->ID)
    );
}
echo json_encode($res, JSON_UNESCAPED_UNICODE);
"""

with sftp.open('dump_posts.php', 'w') as f:
    f.write(php_code)

stdin, stdout, stderr = ssh.exec_command('LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php dump_posts.php && rm dump_posts.php')
out = stdout.read().decode('utf-8', errors='replace')
sftp.close()
ssh.close()

data = json.loads(out)
with open('posts_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Total posts retrieved: {len(data)}")
for i, p in enumerate(data):
    c_str = ', '.join(p['cat_names'])
    print(f"{i+1:02d}. [{p['status']}] {p['date'][:10]} [{c_str}] ({p['slug']})")
    print(f"    Title: {p['title']}")
    print(f"    URL:   {p['url']}")
