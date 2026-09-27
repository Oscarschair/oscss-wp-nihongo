import os
import re
import sys
import json
import base64
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

ids_to_fetch = [1, 19, 30, 36, 44, 85, 109, 111, 127, 144, 150]

php_code = f"""<?php
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
$ids = json_decode('{json.dumps(ids_to_fetch)}', true);
$res = [];
foreach ($ids as $id) {{
    $p = get_post($id);
    if ($p) {{
        $res[$id] = [
            'ID' => $p->ID,
            'title' => $p->post_title,
            'content' => $p->post_content,
            'excerpt' => $p->post_excerpt,
            'date' => $p->post_date,
            'status' => $p->post_status,
            'name' => $p->post_name
        ];
    }}
}}
echo base64_encode(json_encode($res));
"""

sftp = ssh.open_sftp()
with sftp.open('fetch_posts_content.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php fetch_posts_content.php && rm fetch_posts_content.php')
raw_b64 = stdout.read().decode('utf-8', errors='replace').strip()
posts_dict = json.loads(base64.b64decode(raw_b64).decode('utf-8'))

print(f"Fetched {len(posts_dict)} posts from WordPress.")
with open('wp_fetched_posts.json', 'w', encoding='utf-8') as f:
    json.dump(posts_dict, f, ensure_ascii=False, indent=2)

ssh.close()
print("Saved to wp_fetched_posts.json")
