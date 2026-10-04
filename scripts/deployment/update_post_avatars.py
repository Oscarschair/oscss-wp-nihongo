import os
import re
import sys
import json
import base64
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.abspath(os.getcwd()))
from scripts.core.gutenberg_parser import parse_markdown_to_gutenberg_full

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

# Target mapping: original post IDs 3116..3156
posts_dir = "content/posts"
md_files = sorted([f for f in os.listdir(posts_dir) if f.endswith('.md') and f >= "2026-10-16"])

original_ids = [
    3116, 3118, 3120, 3122, 3124, 3126, 3128, 3130, 3132, 3134,
    3136, 3138, 3140, 3142, 3144, 3146, 3148, 3150, 3152, 3154, 3156
]

def clean_title(title_raw, slug):
    title = re.sub(r'<rt>.*?</rt>', '', title_raw)
    title = re.sub(r'<ruby>(.*?)</ruby>', r'\1', title)
    title = re.sub(r'<[^>]+>', '', title)
    title = title.strip()

    if 'street-japanese' in slug:
        title = re.sub(r'^(?:ストリート日本語|街角サバイバル)[:：]\s*', '', title)
        title = f"街角サバイバル：{title}"
    elif 'japanese-comparing' in slug:
        title = re.sub(r'^(?:くらべてみました|くらべてみよう)[:：]\s*', '', title)
        title = f"くらべてみました：{title}"
    elif 'kotoba-no-aya' in slug:
        title = re.sub(r'^(?:ことばのあや)[:：]\s*', '', title)
        title = f"ことばのあや：{title}"
    elif 'culture-shock' in slug:
        title = re.sub(r'^(?:カルチャーショック)[:：]\s*', '', title)
        title = f"カルチャーショック：{title}"

    return title

update_payload = []
for post_id, md_file in zip(original_ids, md_files):
    md_path = os.path.join(posts_dir, md_file)
    with open(md_path, 'r', encoding='utf-8') as f:
        raw_md = f.read()

    title_m = re.search(r'title:\s*"([^"]+)"', raw_md)
    desc_m = re.search(r'description:\s*"([^"]+)"', raw_md)
    slug_m = re.search(r'slug:\s*"([^"]+)"', raw_md)

    slug = slug_m.group(1) if slug_m else ""
    title_raw = title_m.group(1) if title_m else ""
    desc = desc_m.group(1) if desc_m else ""

    clean_t = clean_title(title_raw, slug)
    gutenberg_html = parse_markdown_to_gutenberg_full(md_path)

    update_payload.append({
        'ID': post_id,
        'post_title': clean_t,
        'post_content': gutenberg_html,
        'post_excerpt': desc,
        'slug': slug
    })

print(f"Prepared updates with avatar images for {len(update_payload)} posts.")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

# 1. Upload updated main.css to remote theme
remote_theme_base = "web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo"
remote_css = f"{remote_theme_base}/assets/css/main.css"
sftp.put("assets/css/main.css", remote_css)
print(f"[SFTP OK] Uploaded assets/css/main.css to {remote_css}")

# 2. Update post content in WordPress
payload_json = json.dumps(update_payload, ensure_ascii=False)
payload_b64 = base64.b64encode(payload_json.encode('utf-8')).decode('ascii')

php_template = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$b64 = '###PAYLOAD_B64###';
$data = json_decode(base64_decode($b64), true);

if (!$data) {
    echo "ERROR: Failed to decode json payload\\n";
    exit(1);
}

echo "=== Updating posts with avatar images ===" . PHP_EOL;
foreach ($data as $item) {
    $pid = $item['ID'];
    $post_arr = array(
        'ID'           => $pid,
        'post_title'   => $item['post_title'],
        'post_content' => $item['post_content'],
        'post_excerpt' => $item['post_excerpt'],
    );

    $res = wp_update_post($post_arr, true);
    if (is_wp_error($res)) {
        echo "[ERROR] Post " . $pid . ": " . $res->get_error_message() . PHP_EOL;
    } else {
        echo "[UPDATED] Post " . $pid . " (" . $item['slug'] . ") with avatars" . PHP_EOL;
    }
}

// Purge Cache
if (has_action('litespeed_purge_all')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache successfully purged!" . PHP_EOL;
}
"""

php_script = php_template.replace('###PAYLOAD_B64###', payload_b64)

with sftp.open('update_post_avatars.php', 'w') as f:
    f.write(php_script)

print("\nExecuting update_post_avatars.php on remote server...")
stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php update_post_avatars.php && rm update_post_avatars.php', timeout=180)
print(stdout.read().decode('utf-8', errors='replace'))
err = stderr.read().decode('utf-8', errors='replace')
if err:
    print("Stderr:", err)

sftp.close()
ssh.close()
print("Post avatar updates completed successfully!")
