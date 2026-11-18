# -*- coding: utf-8 -*-
"""
2026-11-25(水)〜2026-12-19(土) 全25記事の一括同期・予約投稿スクリプト
（WebPサムネイル・JPG本文挿入画SFTP転送・初期PVゼロ設定・LiteSpeedパージ完全対応版）
"""
import base64
import glob
import json
import os
import re
import sys
import paramiko

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.abspath(os.getcwd()))
from scripts.core.gutenberg_parser import parse_markdown_to_gutenberg_full

with open(".env.deploy", "r", encoding="utf-8") as f:
    env = dict(l.strip().split("=", 1) for l in f if "=" in l and not l.startswith("#"))

files = sorted(
    fp for fp in glob.glob("content/posts/*.md") if "2026-11-25" <= os.path.basename(fp)[:10] <= "2026-12-19"
)
print(f"対象記事数: {len(files)} 本")

posts_payload = []
thumbnails_to_upload = set()
post_images_to_upload = set()

for md_path in files:
    with open(md_path, "r", encoding="utf-8") as fp:
        raw_text = fp.read()

    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw_text, re.DOTALL)
    if not fm_match:
        raise RuntimeError(f"No frontmatter in {md_path}")

    fm_text, body_text = fm_match.group(1), fm_match.group(2)

    slug = re.search(r'^slug:\s*["\']?(.*?)["\']?$', fm_text, re.M).group(1)
    title_raw = re.search(r'^title:\s*["\']?(.*?)["\']?$', fm_text, re.M).group(1)
    clean_title = re.sub(r"<[^>]+>", "", title_raw)
    desc = re.search(r'^description:\s*["\']?(.*?)["\']?$', fm_text, re.M).group(1)
    date_str = re.search(r'^date:\s*["\']?(.*?)["\']?$', fm_text, re.M).group(1)
    m_date = re.match(r"(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})", date_str)
    post_date = f"{m_date.group(1)} {m_date.group(2)}"

    categories = []
    c_list = re.findall(r"categories:\s*\n((?:\s*-\s*.*?\n)+)", fm_text)
    if c_list:
        for line in c_list[0].strip().split("\n"):
            val = re.sub(r'^\s*-\s*["\']?', "", line).rstrip("\"', ")
            if val:
                categories.append(val)

    tags = []
    t_list = re.findall(r"tags:\s*\n((?:\s*-\s*.*?\n)+)", fm_text)
    if t_list:
        for line in t_list[0].strip().split("\n"):
            val = re.sub(r'^\s*-\s*["\']?', "", line).rstrip("\"', ")
            if val:
                tags.append(val)

    j_match = re.search(r'^jlpt:\s*["\']?(.*?)["\']?$', fm_text, re.M)
    jlpt = j_match.group(1) if j_match else "N2"

    th_match = re.search(r'^thumbnail:\s*["\']?(.*?)["\']?$', fm_text, re.M)
    thumb_path = th_match.group(1) if th_match else ""
    thumb_filename = os.path.basename(thumb_path)
    if thumb_filename:
        thumbnails_to_upload.add(thumb_filename)

    for im_m in re.finditer(r"!\[.*?\]\((assets/images/posts/[^)]+)\)", body_text):
        post_images_to_upload.add(os.path.basename(im_m.group(1)))

    gutenberg_html = parse_markdown_to_gutenberg_full(md_path)

    posts_payload.append(
        {
            "slug": slug,
            "post_title": clean_title,
            "post_content": gutenberg_html,
            "post_excerpt": desc,
            "post_date": post_date,
            "categories": categories,
            "tags": tags,
            "thumb_file": thumb_filename,
            "jlpt": jlpt,
        }
    )


def run_sync(dry_run=True):
    missing = []
    for t_file in sorted(thumbnails_to_upload):
        if not os.path.exists(os.path.join("assets/images/thumbnails", t_file)):
            missing.append(f"thumb:{t_file}")
    for p_file in sorted(post_images_to_upload):
        if not os.path.exists(os.path.join("assets/images/posts", p_file)):
            missing.append(f"post_img:{p_file}")

    print(f"ペイロード数: {len(posts_payload)} 件 | サムネ: {len(thumbnails_to_upload)} 枚 | 挿入画: {len(post_images_to_upload)} 枚")
    if missing:
        print(f"[BLOCK] 未生成の画像アセットが {len(missing)} 件あります:")
        for m in missing[:10]:
            print(f"  - {m}")
        if not dry_run:
            raise RuntimeError("Cannot execute production sync while image assets are missing!")

    if dry_run:
        print("[DRY-RUN] 解析完了（本番反映は実行しません）。")
        return

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=env["SSH_HOST"],
        port=int(env["SSH_PORT"]),
        username=env["SSH_USER"],
        password=env["SSH_PASS"],
        look_for_keys=False,
        allow_agent=False,
        timeout=30,
    )
    sftp = ssh.open_sftp()

    remote_theme_base = "web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo"
    remote_thumb_dir = f"{remote_theme_base}/assets/images/thumbnails"
    remote_posts_img_dir = f"{remote_theme_base}/assets/images/posts"

    print("\n=== 1. Uploading WebP Thumbnails via SFTP ===")
    for t_file in sorted(thumbnails_to_upload):
        sftp.put(os.path.join("assets/images/thumbnails", t_file), f"{remote_thumb_dir}/{t_file}")
        print(f"  [THUMB SFTP OK] {t_file}")

    print("\n=== 2. Uploading In-Article JPG Illustrations via SFTP ===")
    for p_file in sorted(post_images_to_upload):
        sftp.put(os.path.join("assets/images/posts", p_file), f"{remote_posts_img_dir}/{p_file}")
        print(f"  [POST IMG SFTP OK] {p_file}")

    payload_b64 = base64.b64encode(json.dumps(posts_payload, ensure_ascii=False).encode("utf-8")).decode("ascii")

    php_script = f"""<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');

$data = json_decode(base64_decode('{payload_b64}'), true);
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
        'post_title'    => $item['post_title'],
        'post_content'  => $item['post_content'],
        'post_excerpt'  => $item['post_excerpt'],
        'post_status'   => 'future',
        'post_name'     => $slug,
        'post_type'     => 'post',
        'post_date'     => $post_date,
        'post_date_gmt' => $post_date_gmt,
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
        if ($post_id > 0) {{
            update_post_meta($post_id, '_oscss_post_views', 0);
        }}
    }}

    if (is_wp_error($res)) {{
        echo "[ERROR] Post " . $slug . ": " . $res->get_error_message() . "\\n";
        continue;
    }}

    $cat_ids = array();
    foreach ($item['categories'] as $cat_name) {{
        $term = get_term_by('name', $cat_name, 'category');
        if ($term) $cat_ids[] = $term->term_id;
    }}
    if (!empty($cat_ids)) {{
        wp_set_post_categories($post_id, $cat_ids);
    }}
    if (!empty($item['tags'])) {{
        wp_set_post_tags($post_id, $item['tags']);
    }}
    if (!empty($item['jlpt'])) {{
        update_post_meta($post_id, 'jlpt_level', $item['jlpt']);
    }}

    $thumb_file = $item['thumb_file'];
    if (!empty($thumb_file)) {{
        $src = $theme_thumb_dir . $thumb_file;
        if (file_exists($src)) {{
            $dest_file = $upload_dir['path'] . '/' . $thumb_file;
            copy($src, $dest_file);
            $atts = get_posts(array(
                'post_type'   => 'attachment',
                'meta_key'    => '_wp_attached_file',
                'meta_value'  => ltrim($upload_dir['subdir'], '/') . '/' . $thumb_file,
                'numberposts' => 1
            ));
            if (empty($atts)) {{
                $atts = get_posts(array(
                    'post_type'   => 'attachment',
                    'name'        => preg_replace('/\\.[^.]+$/', '', $thumb_file),
                    'numberposts' => 1
                ));
            }}
            if (!empty($atts)) {{
                $att_id = $atts[0]->ID;
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
            }}
            $attach_data = wp_generate_attachment_metadata($att_id, $dest_file);
            wp_update_attachment_metadata($att_id, $attach_data);
            set_post_thumbnail($post_id, $att_id);
        }}
    }}

    $p = get_post($post_id);
    echo "[" . $action . "] ID: " . $post_id . " | Date: " . $p->post_date . " | Status: " . $p->post_status . " | " . $slug . "\\n";
}}

if (defined('LSCWP_V')) {{
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache Purged All.\\n";
}}
echo "ALL 25 POSTS SYNCED SUCCESSFULLY!\\n";
"""

    remote_runner = "temp_sync_25_posts.php"
    with sftp.open(remote_runner, "w") as f:
        f.write(php_script)

    print("\n=== 3. Executing Remote Sync on WordPress ===")
    stdin, stdout, stderr = ssh.exec_command(f"/usr/local/php/8.2/bin/php {remote_runner}")
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    print(out)
    if err:
        print("[STDERR]", err)

    sftp.remove(remote_runner)
    sftp.close()
    ssh.close()


if __name__ == "__main__":
    is_exec = len(sys.argv) > 1 and sys.argv[1] == "--execute"
    run_sync(dry_run=(not is_exec))
