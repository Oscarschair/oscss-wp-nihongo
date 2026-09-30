import glob
import re
import os
import sys
import json
import base64
import paramiko

sys.stdout.reconfigure(encoding='utf-8')

def clean_ruby_from_title(title_str):
    cleaned = re.sub(r'<rt>.*?</rt>', '', title_str, flags=re.DOTALL)
    cleaned = re.sub(r'<rp>.*?</rp>', '', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'</?ruby[^>]*>', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

# 1. Collect title mapping from content/posts/*.md and content/manga/*.md
md_files = sorted(glob.glob('content/posts/*.md')) + sorted(glob.glob('content/manga/*.md'))
slug_map = {}

for f in md_files:
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    parts = re.split(r'^---\s*$', c, maxsplit=2, flags=re.MULTILINE)
    if len(parts) >= 3:
        fm = parts[1]
        slug_m = re.search(r'^slug:\s*["\']?(.*?)["\']?$', fm, re.MULTILINE)
        title_m = re.search(r'^title:\s*["\']?(.*?)["\']?$', fm, re.MULTILINE)
        slug = slug_m.group(1).strip() if slug_m else ''
        title = title_m.group(1).strip() if title_m else ''
        if slug and title:
            clean_title = clean_ruby_from_title(title)
            slug_map[slug] = clean_title
            
            # Also without date prefix
            fname = os.path.basename(f)
            base_slug = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', os.path.splitext(fname)[0])
            slug_map[base_slug] = clean_title

print(f"Collected {len(slug_map)} slug-to-title pairs from {len(md_files)} markdown files.")

# 2. Connect to WordPress and update missing titles
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

payload_b64 = base64.b64encode(json.dumps(slug_map, ensure_ascii=False).encode('utf-8')).decode('utf-8')

php_script = f"""<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$b64 = '{payload_b64}';
$mapping = json_decode(base64_decode($b64), true);

$posts = get_posts(array(
    'numberposts' => -1,
    'post_type' => 'post',
    'post_status' => array('publish', 'future', 'draft')
));

$updated = 0;
foreach ($posts as $p) {{
    $slug = $p->post_name;
    $curr_title = trim($p->post_title);
    
    // Check if title is empty or needs update
    $target_title = null;
    if (isset($mapping[$slug])) {{
        $target_title = $mapping[$slug];
    }} else {{
        foreach ($mapping as $s => $t) {{
            if (strpos($s, $slug) === 0 || strpos($slug, $s) === 0) {{
                $target_title = $t;
                break;
            }}
        }}
    }}
    
    if ($target_title && (empty($curr_title) || $curr_title !== $target_title)) {{
        wp_update_post(array(
            'ID' => $p->ID,
            'post_title' => $target_title
        ));
        echo "Updated Post #{{$p->ID}} (slug: {{$slug}}) -> '{{$target_title}}'\\n";
        $updated++;
    }}
}}

if (defined('LSCWP_V')) {{
    do_action('litespeed_purge_all');
}}
if (function_exists('opcache_reset')) {{
    @opcache_reset();
}}

echo "FINISHED: Total updated posts = {{$updated}}\\n";
"""

remote_php = 'web/nihongo.oscarchair.jp/temp_restore_titles.php'
with sftp.file(remote_php, 'w') as f:
    f.write(php_script)

stdin, stdout, stderr = ssh.exec_command(f'LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php $HOME/{remote_php} && rm -f $HOME/{remote_php}')
output = stdout.read().decode('utf-8', errors='ignore')
print(output)
sftp.close()
ssh.close()
