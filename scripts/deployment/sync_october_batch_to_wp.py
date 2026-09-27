import os
import re
import sys
import base64
import json
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.abspath(os.getcwd()))
from scripts.core.gutenberg_parser import parse_markdown_to_gutenberg_full

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

targets = [
    (618, "content/posts/2026-10-01-street-japanese-kaitenzushi-hot-water-express-lane-survival-guide.md"),
    (620, "content/posts/2026-10-02-japanese-comparing-futoru-futotteiru-aspect-differences.md"),
    (622, "content/posts/2026-10-03-street-japanese-ramen-ticket-machine-call-survival-guide.md"),
    (1229, "content/posts/2026-10-04-kotoba-no-aya-otsukaresama-vs-gokurousama-trap.md"),
    (1168, "content/posts/2026-10-05-culture-shock-why-no-phone-calls-and-newspapers-on-japanese-trains.md"),
    (1619, "content/posts/2026-10-06-japanese-comparing-iku-vs-kuru-perspective-trap.md"),
    (1621, "content/posts/2026-10-07-street-japanese-delivery-redelivery-undelivered-notice-dungeon-guide.md"),
    (1623, "content/posts/2026-10-08-kotoba-no-aya-the-trap-of-kekkoudesu-yes-or-no.md"),
    (1625, "content/posts/2026-10-09-culture-shock-hanko-seal-stamp-culture-and-signature.md"),
    (1627, "content/posts/2026-10-10-street-japanese-clinic-medical-questionnaire-pharmacy-guide.md"),
    (1629, "content/posts/2026-10-11-japanese-comparing-hazu-vs-wake-nuance-differences.md"),
    (1631, "content/posts/2026-10-12-culture-shock-shoumi-kigen-vs-shouhi-kigen-discount-stickers.md"),
]

def clean_title(title_raw, slug):
    # Remove ruby tags and rt tags
    title = re.sub(r'<rt>.*?</rt>', '', title_raw)
    title = re.sub(r'<ruby>(.*?)</ruby>', r'\1', title)
    title = re.sub(r'<[^>]+>', '', title)
    title = title.strip()

    # Enforce correct series prefix
    if 'street-japanese' in slug:
        # replace any incorrect prefix like ストリート日本語
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

posts_payload = []

for post_id, md_path in targets:
    with open(md_path, 'r', encoding='utf-8') as f:
        raw_md = f.read()

    # Parse frontmatter
    title_m = re.search(r'title:\s*"([^"]+)"', raw_md)
    desc_m = re.search(r'description:\s*"([^"]+)"', raw_md)
    date_m = re.search(r'date:\s*"([^"]+)"', raw_md)
    slug_m = re.search(r'slug:\s*"([^"]+)"', raw_md)

    slug = slug_m.group(1) if slug_m else ""
    title_raw = title_m.group(1) if title_m else ""
    desc = desc_m.group(1) if desc_m else ""
    date_str = date_m.group(1) if date_m else ""

    clean_t = clean_title(title_raw, slug)
    
    # Parse date to MySQL format (YYYY-MM-DD HH:MM:SS)
    # e.g., "2026-10-01T08:00:00+09:00" -> "2026-10-01 08:00:00"
    m_date = re.match(r'(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})', date_str)
    if m_date:
        post_date = f"{m_date.group(1)} {m_date.group(2)}"
    else:
        post_date = ""

    # Generate Gutenberg blocks HTML
    gutenberg_html = parse_markdown_to_gutenberg_full(md_path)

    posts_payload.append({
        'ID': post_id,
        'post_title': clean_t,
        'post_name': slug,
        'post_content': gutenberg_html,
        'post_excerpt': desc,
        'post_date': post_date,
        'post_status': 'future'
    })

print(f"Prepared {len(posts_payload)} posts for sync.")
for p in posts_payload:
    print(f"  ID {p['ID']}: [{p['post_date']}] {p['post_title'][:40]}... (Content len: {len(p['post_content'])} chars)")

# Serialize to JSON and encode in base64
payload_json = json.dumps(posts_payload, ensure_ascii=False)
payload_b64 = base64.b64encode(payload_json.encode('utf-8')).decode('ascii')

# Connect to SSH
print("\nConnecting to SSH server...")
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
print("Connected!")

# Transfer batch sync script
php_sync_script = f"""<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$b64 = '{payload_b64}';
$data = json_decode(base64_decode($b64), true);

if (!$data) {{
    echo "ERROR: Failed to decode json payload\\n";
    exit(1);
}}

foreach ($data as $item) {{
    $post_arr = array(
        'ID'           => $item['ID'],
        'post_title'   => $item['post_title'],
        'post_content' => $item['post_content'],
        'post_excerpt' => $item['post_excerpt'],
        'post_status'  => 'future'
    );

    if (!empty($item['post_date'])) {{
        $post_arr['post_date'] = $item['post_date'];
        // Compute GMT date (JST is UTC+9)
        $timestamp = strtotime($item['post_date']) - (9 * 3600);
        $post_arr['post_date_gmt'] = gmdate('Y-m-d H:i:s', $timestamp);
    }}

    $res = wp_update_post($post_arr, true);
    if (is_wp_error($res)) {{
        echo "[ERROR] Post " . $item['ID'] . ": " . $res->get_error_message() . "\\n";
    }} else {{
        $p = get_post($item['ID']);
        $read_time = function_exists('oscss_get_reading_time') ? oscss_get_reading_time($p) : 0;
        echo "[UPDATED] Post " . $item['ID'] . " | Date: " . $p->post_date . " | Status: " . $p->post_status . " | Title: " . mb_substr($p->post_title, 0, 30) . "... | Reading time: 約" . $read_time . "分\\n";
    }}
}}

// Purge LiteSpeed Cache
if (has_action('litespeed_purge_all')) {{
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache successfully purged!\\n";
}}
"""

with sftp.open('sync_batch_october.php', 'w') as f:
    f.write(php_sync_script)

print("\nExecuting sync_batch_october.php on remote server...")
stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php sync_batch_october.php && rm sync_batch_october.php', timeout=60)
print(stdout.read().decode('utf-8', errors='replace'))
err = stderr.read().decode('utf-8', errors='replace')
if err:
    print("Stderr:", err)

sftp.close()
ssh.close()
print("Batch sync completed successfully!")
