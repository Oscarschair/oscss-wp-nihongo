# -*- coding: utf-8 -*-
"""
11/06(金)〜11/19(木) 全14記事の一括同期・予約投稿スクリプト（WebPサムネイル完全対応版）
"""
import paramiko
import sys
import os
import glob
import re
import json
import base64

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.abspath(os.getcwd()))
from scripts.core.gutenberg_parser import parse_markdown_to_gutenberg_full

print("=== 1. 環境変数の読み込み ===")
with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

print("=== 2. 11/06〜11/19 全14記事のMarkdown解析とペイロード構築 ===")
files = sorted(glob.glob('content/posts/2026-11-*.md'))[5:] # 11-06 to 11-19
print(f"対象記事数: {len(files)} 本")

posts_payload = []
thumbnails_to_upload = set()

for md_path in files:
    with open(md_path, 'r', encoding='utf-8') as fp:
        raw_text = fp.read()

    # Frontmatter extraction
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', raw_text, re.DOTALL)
    if not fm_match:
        print(f"[WARN] No frontmatter in {md_path}")
        continue
    
    fm_text = fm_match.group(1)

    # Slug
    s_match = re.search(r'^slug:\s*["\']?(.*?)["\']?$', fm_text, re.MULTILINE)
    slug = s_match.group(1) if s_match else ""

    # Title (clean for WP title)
    t_match = re.search(r'^title:\s*["\']?(.*?)["\']?$', fm_text, re.MULTILINE)
    title = t_match.group(1) if t_match else ""
    clean_title = re.sub(r'<[^>]+>', '', title)

    # Description
    d_match = re.search(r'^description:\s*["\']?(.*?)["\']?$', fm_text, re.MULTILINE)
    desc = d_match.group(1) if d_match else ""

    # Date
    dt_match = re.search(r'^date:\s*["\']?(.*?)["\']?$', fm_text, re.MULTILINE)
    date_str = dt_match.group(1) if dt_match else ""
    m_date = re.match(r'(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})', date_str)
    post_date = f"{m_date.group(1)} {m_date.group(2)}" if m_date else ""

    # Categories
    categories = []
    c_list = re.findall(r'categories:\s*\n((?:\s*-\s*.*?\n)+)', fm_text)
    if c_list:
        for line in c_list[0].strip().split('\n'):
            val = re.sub(r'^\s*-\s*["\']?', '', line).rstrip('"\', ')
            if val:
                categories.append(val)
    if not categories:
        c_match = re.search(r'^category:\s*["\']?(.*?)["\']?$', fm_text, re.MULTILINE)
        if c_match:
            categories.append(c_match.group(1))

    # Tags
    tags = []
    t_list = re.findall(r'tags:\s*\n((?:\s*-\s*.*?\n)+)', fm_text)
    if t_list:
        for line in t_list[0].strip().split('\n'):
            val = re.sub(r'^\s*-\s*["\']?', '', line).rstrip('"\', ')
            if val:
                tags.append(val)

    # JLPT
    j_match = re.search(r'^jlpt:\s*["\']?(.*?)["\']?$', fm_text, re.MULTILINE)
    jlpt = j_match.group(1) if j_match else ""

    # Thumbnail (WebP)
    th_match = re.search(r'^thumbnail:\s*["\']?(.*?)["\']?$', fm_text, re.MULTILINE)
    thumb_path = th_match.group(1) if th_match else ""
    thumb_filename = os.path.basename(thumb_path)
    if thumb_filename:
        thumbnails_to_upload.add(thumb_filename)

    # Gutenberg HTML conversion
    gutenberg_html = parse_markdown_to_gutenberg_full(md_path)

    posts_payload.append({
        'slug': slug,
        'post_title': clean_title,
        'post_content': gutenberg_html,
        'post_excerpt': desc,
        'post_date': post_date,
        'categories': categories,
        'tags': tags,
        'thumb_file': thumb_filename,
        'jlpt': jlpt
    })

print(f"解析完了: {len(posts_payload)} 件の記事ペイロード作成")
print(f"アップロード対象WebPサムネイル: {len(thumbnails_to_upload)} 件")

def run_sync(dry_run=True):
    if dry_run:
        print("\n[DRY-RUN] 本番反映は行いません。解析データのみ検証完了。")
        for p in posts_payload:
            print(f"  - {p['post_date']} | {p['slug']} | Thumb: {p['thumb_file']}")
        return

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
    print("Connected to SSH/SFTP!")

    remote_theme_base = "web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo"
    remote_thumb_dir = f"{remote_theme_base}/assets/images/thumbnails"

    # Upload WebP Thumbnails
    print("\n=== Uploading WebP Thumbnails via SFTP ===")
    for t_file in sorted(thumbnails_to_upload):
        local_path = os.path.join("assets/images/thumbnails", t_file)
        remote_path = f"{remote_thumb_dir}/{t_file}"
        if os.path.exists(local_path):
            sftp.put(local_path, remote_path)
            print(f"  [SFTP OK] {t_file}")
        else:
            print(f"  [WARN] Local thumbnail not found: {local_path}")

    # Prepare Remote PHP Script for Sync & Schedule
    payload_json = json.dumps(posts_payload, ensure_ascii=False)
    payload_b64 = base64.b64encode(payload_json.encode('utf-8')).decode('ascii')

    php_script = f"""<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');

$b64 = '{payload_b64}';
$data = json_decode(base64_decode($b64), true);

if (!$data) {{
    echo "ERROR: Failed to decode json payload\\n";
    exit(1);
}}

$theme_thumb_dir = getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/thumbnails/';
$upload_dir = wp_upload_dir();

foreach ($data as $item) {{
    $slug = $item['slug'];
    $post_date = $item['post_date'];
    $timestamp = strtotime($post_date) - (9 * 3600);
    $post_date_gmt = gmdate('Y-m-d H:i:s', $timestamp);

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

    if (!empty($existing)) {{
        $post_id = $existing[0]->ID;
        $post_arr['ID'] = $post_id;
        $res = wp_update_post($post_arr, true);
        $action = "UPDATED";
    }} else {{
        $res = wp_insert_post($post_arr, true);
        $post_id = is_wp_error($res) ? 0 : $res;
        $action = "INSERTED";
    }}

    if (is_wp_error($res)) {{
        echo "[ERROR] Post " . $slug . ": " . $res->get_error_message() . "\\n";
        continue;
    }}

    // Categories
    $cat_ids = array();
    if (!empty($item['categories'])) {{
        $cat_alias = [
            '言葉のあや' => 'ことばのあや',
            '日本語比べ' => 'くらべてみました',
            'ストリート日本語' => '街角サバイバル',
        ];
        foreach ($item['categories'] as $cat_name) {{
            $normalized_name = isset($cat_alias[$cat_name]) ? $cat_alias[$cat_name] : $cat_name;
            $term = get_term_by('name', $normalized_name, 'category');
            if (!$term) {{
                $term = get_term_by('slug', $normalized_name, 'category');
            }}
            if ($term) {{
                $cat_ids[] = $term->term_id;
            }}
        }}
    }}
    if (empty($cat_ids)) {{
        if (strpos($slug, 'street-japanese') !== false) {{
            $t = get_category_by_slug('street-japanese');
            if ($t) $cat_ids[] = $t->term_id;
        }} elseif (strpos($slug, 'comparing') !== false) {{
            $t = get_category_by_slug('comparing');
            if ($t) $cat_ids[] = $t->term_id;
        }} elseif (strpos($slug, 'kotoba-no-aya') !== false) {{
            $t = get_category_by_slug('kotoba-no-aya');
            if ($t) $cat_ids[] = $t->term_id;
        }} elseif (strpos($slug, 'culture-shock') !== false) {{
            $t = get_category_by_slug('culture-shock');
            if ($t) $cat_ids[] = $t->term_id;
        }}
    }}
    if (!empty($cat_ids)) {{
        wp_set_post_categories($post_id, $cat_ids);
    }}

    // Tags
    if (!empty($item['tags'])) {{
        wp_set_post_tags($post_id, $item['tags']);
    }}

    // JLPT
    if (!empty($item['jlpt'])) {{
        update_post_meta($post_id, 'jlpt_level', $item['jlpt']);
    }}

    // Set Thumbnail (WebP)
    $thumb_file = $item['thumb_file'];
    if (!empty($thumb_file)) {{
        $src = $theme_thumb_dir . $thumb_file;
        if (file_exists($src)) {{
            $dest_file = $upload_dir['path'] . '/' . $thumb_file;
            copy($src, $dest_file);

            $atts = get_posts(array(
                'post_type'   => 'attachment',
                'meta_key'    => '_wp_attached_file',
                'meta_value'  => $thumb_file,
                'numberposts' => 1
            ));

            if (!empty($atts)) {{
                $att_id = $atts[0]->ID;
                $attach_data = wp_generate_attachment_metadata($att_id, $dest_file);
                wp_update_attachment_metadata($att_id, $attach_data);
            }} else {{
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
            }}

            set_post_thumbnail($post_id, $att_id);
        }}
    }}

    $p = get_post($post_id);
    echo "[" . $action . "] ID: " . $post_id . " | Date: " . $p->post_date . " | Status: " . $p->post_status . " | " . $slug . "\\n";
}}

// Purge LiteSpeed Cache
if (defined('LSCWP_V')) {{
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache Purged All.\\n";
}}
echo "ALL DONE SUCCESS!\\n";
"""

    remote_runner_path = "temp_sync_14_posts.php"
    with sftp.open(remote_runner_path, "w") as f:
        f.write(php_script)
    print("Uploaded runner php.")

    print("\n=== Executing Remote Sync on WordPress ===")
    stdin, stdout, stderr = ssh.exec_command(f"/usr/local/php/8.2/bin/php {remote_runner_path}")
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print("[STDERR]", err)

    sftp.remove(remote_runner_path)
    sftp.close()
    ssh.close()
    print("=== Sync completed! ===")

if __name__ == '__main__':
    is_execute = len(sys.argv) > 1 and sys.argv[1] == '--execute'
    run_sync(dry_run=(not is_execute))
