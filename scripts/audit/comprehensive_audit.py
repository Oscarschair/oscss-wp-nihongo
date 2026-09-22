import os
import json
import sys
import urllib.request
import paramiko

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

print('=== 1. REMOTE THEME ASSETS AUDIT ===')
remote_theme = 'web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/'
for sub in ['assets/images/thumbnails', 'assets/images/posts']:
    path = remote_theme + sub
    flist = sftp.listdir(path)
    dups = [f for f in flist if '-v2' in f or '_v2' in f or '-v3' in f]
    print(f'Remote {sub}: total {len(flist)} files, duplicates: {dups}')

print('\n=== 2. WORDPRESS DATABASE POSTS AUDIT ===')
php_audit = r'''<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$posts = get_posts(array(
    'post_type' => 'post',
    'post_status' => array('future', 'publish'),
    'numberposts' => 12,
    'orderby' => 'date',
    'order' => 'DESC'
));

$res = array();
foreach ($posts as $p) {
    $thumb_id = get_post_thumbnail_id($p->ID);
    $thumb_url = $thumb_id ? wp_get_attachment_url($thumb_id) : '';
    
    // Extract images from post_content
    preg_match_all('/<img[^>]+src=[\'"]([^\'"]+)[\'"]/i', $p->post_content, $matches);
    $content_imgs = !empty($matches[1]) ? $matches[1] : array();
    
    $has_mermaid = (strpos($p->post_content, 'flowchart') !== false || strpos($p->post_content, 'mermaid') !== false);

    $res[] = array(
        'id' => $p->ID,
        'title' => $p->post_title,
        'slug' => $p->post_name,
        'date' => $p->post_date,
        'status' => $p->post_status,
        'thumb_id' => $thumb_id,
        'thumb_url' => $thumb_url,
        'content_imgs' => $content_imgs,
        'has_mermaid' => $has_mermaid
    );
}

echo json_encode($res, JSON_UNESCAPED_UNICODE);
'''

with sftp.open('audit_posts.php', 'w') as f:
    f.write(php_audit)

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php audit_posts.php')
out = stdout.read().decode('utf-8')
err = stderr.read().decode('utf-8')
ssh.exec_command('rm audit_posts.php')

sftp.close()
ssh.close()

if err.strip():
    print('PHP Error:', err)

posts_data = json.loads(out)
for p in posts_data:
    print(f"ID: {p['id']} | Date: {p['date']} | Status: {p['status']}")
    print(f"  Title: {p['title']}")
    print(f"  Slug: {p['slug']}")
    print(f"  Thumb ID: {p['thumb_id']} -> {p['thumb_url']}")
    print(f"  Content Images: {p['content_imgs']}")
    print(f"  Mermaid Leftover: {p['has_mermaid']}")
    print('-' * 60)

print('\n=== 3. LIVE URL HTTP STATUS VERIFICATION ===')
all_urls_to_test = set()
for p in posts_data:
    if p['thumb_url']:
        all_urls_to_test.add(p['thumb_url'])
    for ci in p['content_imgs']:
        if ci.startswith('http'):
            all_urls_to_test.add(ci)

for u in sorted(all_urls_to_test):
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"[OK 200] {u} ({resp.headers.get('Content-Length')} bytes)")
    except Exception as e:
        print(f"[ERROR] {u} -> {e}")
