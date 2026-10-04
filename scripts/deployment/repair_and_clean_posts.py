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
# and duplicate post IDs 3159..3199 to delete
posts_dir = "content/posts"
md_files = sorted([f for f in os.listdir(posts_dir) if f.endswith('.md') and f >= "2026-10-16"])

# Map dates to original IDs
original_ids = [
    3116, 3118, 3120, 3122, 3124, 3126, 3128, 3130, 3132, 3134,
    3136, 3138, 3140, 3142, 3144, 3146, 3148, 3150, 3152, 3154, 3156
]

duplicate_ids = [
    3159, 3161, 3163, 3165, 3167, 3169, 3171, 3173, 3175, 3177,
    3179, 3181, 3183, 3185, 3187, 3189, 3191, 3193, 3195, 3197, 3199
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
    date_m = re.search(r'date:\s*"([^"]+)"', raw_md)
    slug_m = re.search(r'slug:\s*"([^"]+)"', raw_md)
    thumb_m = re.search(r'thumbnail:\s*"([^"]+)"', raw_md)
    jlpt_m = re.search(r'jlpt:\s*"([^"]+)"', raw_md)

    slug = slug_m.group(1) if slug_m else ""
    title_raw = title_m.group(1) if title_m else ""
    desc = desc_m.group(1) if desc_m else ""
    date_str = date_m.group(1) if date_m else ""
    thumb_path = thumb_m.group(1) if thumb_m else ""
    jlpt = jlpt_m.group(1) if jlpt_m else ""

    clean_t = clean_title(title_raw, slug)

    m_date = re.match(r'(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})', date_str)
    post_date = f"{m_date.group(1)} {m_date.group(2)}" if m_date else ""

    thumb_filename = os.path.basename(thumb_path)
    gutenberg_html = parse_markdown_to_gutenberg_full(md_path)

    update_payload.append({
        'ID': post_id,
        'slug': slug,
        'post_title': clean_t,
        'post_content': gutenberg_html,
        'post_excerpt': desc,
        'post_date': post_date,
        'thumb_file': thumb_filename,
        'jlpt': jlpt
    })

print(f"Prepared updates for {len(update_payload)} posts.")
print(f"Prepared deletion for {len(duplicate_ids)} duplicate posts.")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

payload_json = json.dumps({
    'delete_ids': duplicate_ids,
    'updates': update_payload
}, ensure_ascii=False)
payload_b64 = base64.b64encode(payload_json.encode('utf-8')).decode('ascii')

php_template = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');

$b64 = '###PAYLOAD_B64###';
$data = json_decode(base64_decode($b64), true);

if (!$data) {
    echo "ERROR: Failed to decode json payload\\n";
    exit(1);
}

// 1. Delete duplicate posts
echo "=== Deleting duplicate posts ===" . PHP_EOL;
foreach ($data['delete_ids'] as $del_id) {
    $res = wp_delete_post($del_id, true);
    if ($res) {
        echo "Deleted duplicate post ID: " . $del_id . PHP_EOL;
    }
}

// 2. Update original posts with clean content and set thumbnails
$theme_thumb_dir = getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/thumbnails/';
$upload_dir = wp_upload_dir();

echo "=== Updating original posts ===" . PHP_EOL;
foreach ($data['updates'] as $item) {
    $pid = $item['ID'];
    $post_date = $item['post_date'];
    $timestamp = strtotime($post_date) - (9 * 3600);
    $post_date_gmt = gmdate('Y-m-d H:i:s', $timestamp);

    $post_arr = array(
        'ID'           => $pid,
        'post_title'   => $item['post_title'],
        'post_content' => $item['post_content'],
        'post_excerpt' => $item['post_excerpt'],
        'post_name'    => $item['slug'],
        'post_status'  => 'future',
        'post_date'    => $post_date,
        'post_date_gmt'=> $post_date_gmt,
    );

    $res = wp_update_post($post_arr, true);
    if (is_wp_error($res)) {
        echo "[ERROR] Post " . $pid . ": " . $res->get_error_message() . PHP_EOL;
        continue;
    }

    // Set thumbnail
    $thumb_file = $item['thumb_file'];
    if (!empty($thumb_file)) {
        $dest_file = $upload_dir['path'] . '/' . $thumb_file;
        $src = $theme_thumb_dir . $thumb_file;
        if (!file_exists($dest_file) && file_exists($src)) {
            copy($src, $dest_file);
        }

        if (file_exists($dest_file)) {
            // Find attachment
            $atts = get_posts(array(
                'post_type'   => 'attachment',
                'meta_key'    => '_wp_attached_file',
                'meta_value'  => $thumb_file,
                'numberposts' => 1
            ));

            if (!empty($atts)) {
                $att_id = $atts[0]->ID;
            } else {
                $filetype = wp_check_filetype($thumb_file, null);
                $attachment = array(
                    'guid'           => $upload_dir['url'] . '/' . $thumb_file,
                    'post_mime_type' => $filetype['type'],
                    'post_title'     => preg_replace('/\\.[^.]+$/', '', $thumb_file),
                    'post_content'   => '',
                    'post_status'    => 'inherit'
                );
                $att_id = wp_insert_attachment($attachment, $dest_file, $pid);
                $attach_data = wp_generate_attachment_metadata($att_id, $dest_file);
                wp_update_attachment_metadata($att_id, $attach_data);
            }

            set_post_thumbnail($pid, $att_id);
        }
    }

    $p = get_post($pid);
    $read_time = function_exists('oscss_get_reading_time') ? oscss_get_reading_time($p) : 0;
    $has_thumb = has_post_thumbnail($pid) ? "Thumb: OK" : "Thumb: MISSING";
    echo "[UPDATED] ID: " . $pid . " | " . $p->post_date . " | " . $p->post_status . " | " . $has_thumb . " | 約" . $read_time . "分 | " . $item['slug'] . PHP_EOL;
}

// 3. Purge Cache
if (has_action('litespeed_purge_all')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache successfully purged!" . PHP_EOL;
}
"""

php_script = php_template.replace('###PAYLOAD_B64###', payload_b64)

with sftp.open('repair_and_clean_posts.php', 'w') as f:
    f.write(php_script)

print("\nExecuting repair_and_clean_posts.php on remote server...")
stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php repair_and_clean_posts.php && rm repair_and_clean_posts.php', timeout=300)
print(stdout.read().decode('utf-8', errors='replace'))
err = stderr.read().decode('utf-8', errors='replace')
if err:
    print("Stderr:", err)

sftp.close()
ssh.close()
print("Post repair completed!")
