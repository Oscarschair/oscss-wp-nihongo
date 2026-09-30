import paramiko
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

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
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$posts = get_posts(array(
    'numberposts' => -1,
    'post_type' => 'post',
    'post_status' => array('publish', 'future', 'draft')
));

$res = array();
foreach ($posts as $p) {
    $res[] = array(
        'id' => $p->ID,
        'title' => $p->post_title,
        'slug' => $p->post_name,
        'status' => $p->post_status,
        'date' => $p->post_date,
    );
}

echo json_encode($res, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
"""

remote_php = 'web/nihongo.oscarchair.jp/temp_dump_posts.php'
with sftp.file(remote_php, 'w') as f:
    f.write(php_code)

stdin, stdout, stderr = ssh.exec_command(f'LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php $HOME/{remote_php} && rm -f $HOME/{remote_php}')
output = stdout.read().decode('utf-8', errors='ignore')
sftp.close()
ssh.close()

data = json.loads(output)
print(f"Total posts: {len(data)}")
empty_titles = [p for p in data if not p['title'] or not p['title'].strip()]
print(f"Posts with empty title: {len(empty_titles)}")

for p in empty_titles:
    print(f"- ID {p['id']}: slug='{p['slug']}', date='{p['date']}'")
