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

# 1. Load env
with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

# 2. Gather 21 post markdown files
posts_dir = "content/posts"
md_files = sorted([f for f in os.listdir(posts_dir) if f.endswith('.md') and f >= "2026-10-16"])

print(f"Targeting {len(md_files)} posts from 2026-10-16 onwards:")

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

posts_payload = []
thumbnails_to_upload = set()

for md_file in md_files:
    md_path = os.path.join(posts_dir, md_file)
    with open(md_path, 'r', encoding='utf-8') as f:
        raw_md = f.read()

    # Frontmatter regex
    title_m = re.search(r'title:\s*"([^"]+)"', raw_md)
    desc_m = re.search(r'description:\s*"([^"]+)"', raw_md)
    date_m = re.search(r'date:\s*"([^"]+)"', raw_md)
    slug_m = re.search(r'slug:\s*"([^"]+)"', raw_md)
    thumb_m = re.search(r'thumbnail:\s*"([^"]+)"', raw_md)
    jlpt_m = re.search(r'jlpt:\s*"([^"]+)"', raw_md)

    cat_m = re.search(r'categories:\s*\n((?:\s*-\s*"[^"]+"\s*\n)+)', raw_md)
    categories = []
    if cat_m:
        categories = re.findall(r'-\s*"([^"]+)"', cat_m.group(1))

    tags_m = re.search(r'tags:\s*\n((?:\s*-\s*.*?\n)+)', raw_md)
    tags = []
    if tags_m:
        tags = [t.strip().strip('"').strip("'") for t in re.findall(r'-\s*(.+)', tags_m.group(1))]

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
    if thumb_filename:
        thumbnails_to_upload.add(thumb_filename)
        base_name = os.path.splitext(thumb_filename)[0]
        thumbnails_to_upload.add(f"{base_name}.webp")

    gutenberg_html = parse_markdown_to_gutenberg_full(md_path)

    posts_payload.append({
        'slug': slug,
        'post_title': clean_t,
        'post_content': gutenberg_html,
        'post_excerpt': desc,
        'post_date': post_date,
        'categories': categories,
        'tags': tags,
        'thumb_file': thumb_filename,
        'jlpt': jlpt
    })

print(f"Payload created for {len(posts_payload)} posts.")
print(f"Found {len(thumbnails_to_upload)} thumbnail files to upload.")

# 3. Connect to SSH/SFTP
print("\nConnecting to SSH server...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    hostname=env['SSH_HOST'],
    port=int(env['SSH_PORT']),
    username=env['SSH_USER'],
    password=env['SSH_PASS'],
    look_for_keys=False,
    allow_agent=False,
    timeout=30
)
sftp = ssh.open_sftp()
print("Connected!")

remote_theme_base = "web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo"
remote_thumb_dir = f"{remote_theme_base}/assets/images/thumbnails"

# 4. Upload Thumbnails
print("\n=== Uploading Thumbnails via SFTP ===")
for t_file in sorted(thumbnails_to_upload):
    local_path = os.path.join("assets/images/thumbnails", t_file)
    remote_path = f"{remote_thumb_dir}/{t_file}"
    if os.path.exists(local_path):
        sftp.put(local_path, remote_path)
        print(f"  [SFTP OK] {t_file}")
    else:
        print(f"  [WARN] Local thumbnail not found: {local_path}")

# 5. Prepare Remote PHP Script for Sync & Schedule
payload_json = json.dumps(posts_payload, ensure_ascii=False)
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

$theme_thumb_dir = getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/thumbnails/';
$upload_dir = wp_upload_dir();

foreach ($data as $item) {
    $slug = $item['slug'];
    $post_date = $item['post_date'];
    $timestamp = strtotime($post_date) - (9 * 3600);
    $post_date_gmt = gmdate('Y-m-d H:i:s', $timestamp);

    // 1. Check existing post by slug
    $existing = get_posts(array(
        'name'        => $slug,
        'post_type'   => 'post',
        'post_status' => 'any',
        'numberposts' => 1
    ));

    $post_arr = array(
        'post_title'   => $item['post_title'],
        'post_content' => $item['post_content'],
        'post_excerpt' => $item['post_excerpt'],
        'post_status'  => 'future',
        'post_name'    => $slug,
        'post_type'    => 'post',
        'post_date'    => $post_date,
        'post_date_gmt'=> $post_date_gmt,
    );

    if (!empty($existing)) {
        $post_id = $existing[0]->ID;
        $post_arr['ID'] = $post_id;
        $res = wp_update_post($post_arr, true);
        $action = "UPDATED";
    } else {
        $res = wp_insert_post($post_arr, true);
        $post_id = is_wp_error($res) ? 0 : $res;
        $action = "INSERTED";
    }

    if (is_wp_error($res)) {
        echo "[ERROR] Post " . $slug . ": " . $res->get_error_message() . "\\n";
        continue;
    }

    // 2. Set Categories
    $cat_ids = array();
    if (!empty($item['categories'])) {
        $cat_alias = [
            '言葉のあや' => 'ことばのあや',
            '日本語比べ' => 'くらべてみました',
            'ストリート日本語' => '街角サバイバル',
        ];
        foreach ($item['categories'] as $cat_name) {
            $normalized_name = isset($cat_alias[$cat_name]) ? $cat_alias[$cat_name] : $cat_name;
            $term = get_term_by('name', $normalized_name, 'category');
            if (!$term) {
                $term = get_term_by('slug', $normalized_name, 'category');
            }
            if ($term) {
                $cat_ids[] = $term->term_id;
            }
        }
    }
    if (empty($cat_ids)) {
        // Fallback by slug
        if (strpos($slug, 'street-japanese') !== false) {
            $t = get_category_by_slug('street-japanese');
            if ($t) $cat_ids[] = $t->term_id;
        } elseif (strpos($slug, 'comparing') !== false) {
            $t = get_category_by_slug('comparing');
            if ($t) $cat_ids[] = $t->term_id;
        } elseif (strpos($slug, 'kotoba-no-aya') !== false) {
            $t = get_category_by_slug('kotoba-no-aya');
            if ($t) $cat_ids[] = $t->term_id;
        } elseif (strpos($slug, 'culture-shock') !== false) {
            $t = get_category_by_slug('culture-shock');
            if ($t) $cat_ids[] = $t->term_id;
        }
    }
    if (!empty($cat_ids)) {
        wp_set_post_categories($post_id, $cat_ids);
    }

    // 3. Set Tags
    if (!empty($item['tags'])) {
        wp_set_post_tags($post_id, $item['tags']);
    }

    // 4. Set JLPT meta
    if (!empty($item['jlpt'])) {
        update_post_meta($post_id, 'jlpt_level', $item['jlpt']);
    }

    // 5. Set Thumbnail / Featured Image
    $thumb_file = $item['thumb_file'];
    if (!empty($thumb_file)) {
        $src = $theme_thumb_dir . $thumb_file;
        if (file_exists($src)) {
            $dest_file = $upload_dir['path'] . '/' . $thumb_file;
            copy($src, $dest_file);

            // Check existing attachment
            $atts = get_posts(array(
                'post_type'   => 'attachment',
                'meta_key'    => '_wp_attached_file',
                'meta_value'  => $thumb_file,
                'numberposts' => 1
            ));

            if (!empty($atts)) {
                $att_id = $atts[0]->ID;
                $attach_data = wp_generate_attachment_metadata($att_id, $dest_file);
                wp_update_attachment_metadata($att_id, $attach_data);
            } else {
                $filetype = wp_check_filetype($thumb_file, null);
                $attachment = array(
                    'guid'           => $upload_dir['url'] . '/' . $thumb_file,
                    'post_mime_type' => $filetype['type'],
                    'post_title'     => preg_replace('/\\.[^.]+$/', '', $thumb_file),
                    'post_content'   => '',
                    'post_status'    => 'inherit'
                );
                $att_id = wp_insert_attachment($attachment, $dest_file, $post_id);
                $attach_data = wp_generate_attachment_metadata($att_id, $dest_file);
                wp_update_attachment_metadata($att_id, $attach_data);
            }

            set_post_thumbnail($post_id, $att_id);
        }
    }

    $p = get_post($post_id);
    $read_time = function_exists('oscss_get_reading_time') ? oscss_get_reading_time($p) : 0;
    echo "[" . $action . "] ID: " . $post_id . " | Date: " . $p->post_date . " | Status: " . $p->post_status . " | Read: 約" . $read_time . "分 | " . $slug . "\\n";
}

// 6. Purge LiteSpeed Cache
if (has_action('litespeed_purge_all')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache successfully purged!\\n";
}
"""

php_script = php_template.replace('###PAYLOAD_B64###', payload_b64)

with sftp.open('sync_and_schedule_21_posts.php', 'w') as f:
    f.write(php_script)

print("\nExecuting sync_and_schedule_21_posts.php on remote server...")
stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php sync_and_schedule_21_posts.php && rm sync_and_schedule_21_posts.php', timeout=300)
print(stdout.read().decode('utf-8', errors='replace'))
err = stderr.read().decode('utf-8', errors='replace')
if err:
    print("Stderr:", err)

sftp.close()
ssh.close()
print("\nAll 21 posts synced and scheduled successfully!")
