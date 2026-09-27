import os
import glob
import re
import sys
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

# 10月前半のMarkdownファイル
oct_files = sorted(glob.glob('content/posts/2026-10-0[1-9]*.md') + glob.glob('content/posts/2026-10-1[0-2]*.md'))
print(f"Found {len(oct_files)} October early posts:")
slug_to_file = {}
for f in oct_files:
    content = open(f, 'r', encoding='utf-8').read()
    m = re.search(r'^slug:\s*["\']?(.*?)["\']?$', content, re.MULTILINE)
    slug = m.group(1) if m else os.path.basename(f)[11:-3]
    slug_to_file[slug] = f
    print(f"  - {slug} -> {f}")

# WordPress本番DBからPost IDを取得
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    env['SSH_HOST'], 
    int(env['SSH_PORT']), 
    env['SSH_USER'], 
    env['SSH_PASS'], 
    timeout=15,
    look_for_keys=False,
    allow_agent=False
)

php_code = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

global $wpdb;
$slugs = array('""" + "','".join(slug_to_file.keys()) + """');
$in = "'" . implode("','", array_map('esc_sql', $slugs)) . "'";
$rows = $wpdb->get_results("SELECT ID, post_name, post_status, post_date FROM {$wpdb->posts} WHERE post_name IN ($in) AND post_type = 'post'");
foreach ($rows as $r) {
    echo $r->ID . ' | ' . $r->post_status . ' | ' . $r->post_date . ' | ' . $r->post_name . PHP_EOL;
}
"""

sftp = ssh.open_sftp()
with sftp.file('/tmp/get_oct_ids.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php /tmp/get_oct_ids.php')
out = stdout.read().decode('utf-8')
print("Live WordPress Post Mapping:")
print(out)
ssh.close()
