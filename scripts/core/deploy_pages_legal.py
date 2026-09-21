import paramiko
import re
import json
import base64
import sys

sys.stdout.reconfigure(encoding='utf-8')

env_data = {}
with open('.env.deploy', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env_data[k.strip()] = v.strip()

host = env_data.get('SSH_HOST', 'ssh.lolipop.jp')
port = int(env_data.get('SSH_PORT', 2222))
user = env_data.get('SSH_USER')
password = env_data.get('SSH_PASS')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=host, port=port, username=user, password=password, look_for_keys=False, allow_agent=False)

def md_to_gutenberg(md_text):
    body = re.sub(r'^---[\s\S]*?---', '', md_text).strip()
    lines = body.split('\n')
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.strip() == '---':
            blocks.append('<!-- wp:separator {"className":"is-style-wide"} -->\n<hr class="wp-block-separator has-alpha-channel-opacity is-style-wide"/>\n<!-- /wp:separator -->')
            i += 1
            continue
        if line.startswith('# '):
            i += 1
            continue
        if line.startswith('### '):
            t = line[4:].strip()
            blocks.append(f'<!-- wp:heading {{"level":3}} -->\n<h3 class="wp-block-heading">{t}</h3>\n<!-- /wp:heading -->')
            i += 1
            continue
        if line.startswith('## '):
            t = line[3:].strip()
            blocks.append(f'<!-- wp:heading {{"level":2}} -->\n<h2 class="wp-block-heading">{t}</h2>\n<!-- /wp:heading -->')
            i += 1
            continue
        if line.strip().startswith('* ') or line.strip().startswith('- '):
            items = []
            while i < len(lines) and (lines[i].strip().startswith('* ') or lines[i].strip().startswith('- ')):
                item_t = re.sub(r'^[\*\-]\s+', '', lines[i].strip())
                # format markdown link
                item_t = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', item_t)
                item_t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', item_t)
                items.append(f'<li>{item_t}</li>')
                i += 1
            blocks.append(f'<!-- wp:list -->\n<ul>{"".join(items)}</ul>\n<!-- /wp:list -->')
            continue
        p_lines = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(('#', '---', '* ', '- ')):
            pl = lines[i].rstrip()
            pl = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', pl)
            pl = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', pl)
            p_lines.append(pl)
            i += 1
        if p_lines:
            p_text = "<br />\n".join(p_lines)
            blocks.append(f'<!-- wp:paragraph -->\n<p>{p_text}</p>\n<!-- /wp:paragraph -->')
    return "\n\n".join(blocks)

with open('content/pages/privacy-policy.md', 'r', encoding='utf-8') as f:
    privacy_md = f.read()

with open('content/pages/terms.md', 'r', encoding='utf-8') as f:
    terms_md = f.read()

privacy_html = md_to_gutenberg(privacy_md)
terms_html = md_to_gutenberg(terms_md)

payload = [
    {
        "title": "プライバシーポリシー",
        "slug": "privacy-policy",
        "content": privacy_html
    },
    {
        "title": "利用規約",
        "slug": "terms",
        "content": terms_html
    }
]

payload_b64 = base64.b64encode(json.dumps(payload, ensure_ascii=False).encode('utf-8')).decode('utf-8')

php_script = f"""<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$b64 = '{payload_b64}';
$pages = json_decode(base64_decode($b64), true);

foreach ($pages as $p) {{
    $title = $p['title'];
    $slug = $p['slug'];
    $content = $p['content'];
    
    $existing = get_posts(array(
        'name' => $slug,
        'post_type' => 'page',
        'post_status' => 'any',
        'numberposts' => 1
    ));
    
    if (!empty($existing)) {{
        $page_id = $existing[0]->ID;
        wp_update_post(array(
            'ID' => $page_id,
            'post_title' => $title,
            'post_content' => $content,
            'post_status' => 'publish'
        ));
        echo "Updated page $slug (ID: $page_id)\\n";
    }} else {{
        $page_id = wp_insert_post(array(
            'post_title' => $title,
            'post_content' => $content,
            'post_name' => $slug,
            'post_type' => 'page',
            'post_status' => 'publish',
            'post_author' => 1
        ));
        echo "Created page $slug (ID: $page_id)\\n";
    }}
}}

if (defined('LSCWP_V')) {{
    do_action('litespeed_purge_all');
}}
if (function_exists('opcache_reset')) {{
    @opcache_reset();
}}
echo "SUCCESS\\n";
"""

sftp = ssh.open_sftp()
remote_script = 'web/nihongo.oscarchair.jp/deploy_legal_pages_temp.php'
with sftp.open(remote_script, 'w') as f:
    f.write(php_script)

stdin, stdout, stderr = ssh.exec_command(f"/usr/local/php/8.2/bin/php {remote_script}")
print(stdout.read().decode('utf-8'))
sftp.remove(remote_script)
sftp.close()
ssh.close()
