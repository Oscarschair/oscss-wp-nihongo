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
ssh.connect(hostname=env_data['SSH_HOST'], port=int(env_data['SSH_PORT']), username=env_data['SSH_USER'], password=env_data['SSH_PASS'], look_for_keys=False, allow_agent=False)

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
    $res[] = array(
        'date' => $p->post_date,
        'status' => $p->post_status,
        'slug' => $p->post_name,
        'title' => $p->post_title,
        'categories' => $cats
    );
}
echo json_encode($res, JSON_UNESCAPED_UNICODE);
"""

with sftp.open('count_cats.php', 'w') as f:
    f.write(php_code)

stdin, stdout, stderr = ssh.exec_command('LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php count_cats.php && rm count_cats.php')
out = stdout.read().decode('utf-8', errors='replace')
sftp.close()
ssh.close()

data = json.loads(out)
cat_counts = {}
for item in data:
    for c in item['categories']:
        cat_counts[c] = cat_counts.get(c, 0) + 1

print(f"Total posts: {len(data)}")
print("\n=== カテゴリー別累計本数 ===")
for k, v in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"・{k}: {v}件")

print("\n=== 直近の投稿ローテーション（最近6件） ===")
for item in data[-6:]:
    c_str = ','.join(item['categories'])
    print(f"[{item['status']:<7}] {item['date'][:10]} | {c_str:<15} | {item['title'][:35]}")
