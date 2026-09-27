import os
import re
import sys
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

# 10/01 to 10/12 markdown files
post_dates = [f"2026-10-{d:02d}" for d in range(1, 13)]

posts_info = []
for fname in sorted(os.listdir('content/posts')):
    for pd in post_dates:
        if fname.startswith(pd):
            fpath = os.path.join('content/posts', fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            slug_m = re.search(r'slug:\s*"([^"]+)"', content)
            title_m = re.search(r'title:\s*"([^"]+)"', content)
            slug = slug_m.group(1) if slug_m else ""
            title = title_m.group(1) if title_m else ""
            posts_info.append({"date": pd, "file": fname, "slug": slug, "title": title})

print(f"Found {len(posts_info)} target posts in local markdown.")

# Connect to SSH
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    hostname=env['SSH_HOST'],
    port=int(env['SSH_PORT']),
    username=env['SSH_USER'],
    password=env['SSH_PASS'],
    look_for_keys=False,
    allow_agent=False
)

sftp = ssh.open_sftp()
php_query = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
$posts = get_posts(array('numberposts' => -1, 'post_status' => 'any'));
$out = array();
foreach($posts as $p) {
    $out[] = array(
        'ID' => $p->ID,
        'post_name' => $p->post_name,
        'post_status' => $p->post_status,
        'post_date' => $p->post_date,
        'post_title' => $p->post_title
    );
}
echo json_encode($out);
"""
with sftp.open('query_temp.php', 'w') as f:
    f.write(php_query)

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php query_temp.php && rm query_temp.php')
wp_posts = stdout.read().decode('utf-8')
sftp.close()
ssh.close()

import json
remote_posts = json.loads(wp_posts)

print("\n--- Matching Local to Remote ---")
for p in posts_info:
    matched = None
    for rp in remote_posts:
        if rp['post_name'] == p['slug'] or p['date'] in rp['post_date']:
            matched = rp
            break
    if matched:
        print(f"[{p['date']}] Matched ID: {matched['ID']} | Slug: {matched['post_name']} | Status: {matched['post_status']} | Date: {matched['post_date']}")
    else:
        print(f"[{p['date']}] NOT MATCHED! Local slug: {p['slug']}")
