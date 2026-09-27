import os
import shutil
import sys
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 1. Copy generated image to local asset
src_img = r"C:\Users\user\.gemini\antigravity-ide\brain\c8ff313e-4ec8-47e9-b866-72ee31d60fa5\manga_01_daijoubu_v3_1790550683310.jpg"
dst_img = "assets/images/posts/manga-01-daijoubu-trap.jpg"
shutil.copy2(src_img, dst_img)
print(f"Copied {src_img} -> {dst_img}")

# 2. Update local markdown file
md_path = "content/manga/2026-09-11-manga-01-daijoubu-trap.md"
new_md_content = """---
title: "【4コマ漫画】第1話：「大丈夫」はYESなの？NOなの！？｜コンビニ温めトラップ"
description: "コンビニで「お弁当温めますか？」と聞かれ、笑顔で元気よく「大丈夫です！」と答えたオスカー。意気揚々とデスクに戻ってフタを開けると……！？ 日本の魔法の言葉「大丈夫」の二面性を描く4コマ漫画！"
slug: "manga-01-daijoubu-trap"
date: "2026-09-11T09:00:00+09:00"
thumbnail: "assets/images/posts/manga-01-daijoubu-trap.jpg"
connected_slug: "kotoba-no-aya-the-trap-of-daijoubu-yes-or-no-japanese-magic-phrase"
categories:
  - "ことばのあや"
  - "4コマ漫画"
tags:
  - 4コマ漫画
  - 日常会話
  - ニュアンスの違い
  - オスカーの日常
---
"""
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(new_md_content)
print(f"Updated {md_path} (content cleared)")

# 3. Connect to SSH and upload image + update WP post
with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

remote_theme_img = "web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/posts/manga-01-daijoubu-trap.jpg"
sftp.put(dst_img, remote_theme_img)
print(f"Uploaded image to remote: {remote_theme_img}")

# Update WP post ID 2721: clear content, reattach thumbnail
php_code = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');
require_once(ABSPATH . 'wp-admin/includes/file.php');
require_once(ABSPATH . 'wp-admin/includes/media.php');

$post_id = 2721;
$p = get_post($post_id);
if (!$p) {
    // Find by slug if ID changed
    $posts = get_posts([
        'post_type' => 'manga',
        'name' => 'manga-01-daijoubu-trap',
        'post_status' => 'any'
    ]);
    if ($posts) {
        $post_id = $posts[0]->ID;
    }
}

echo "Updating manga post ID: {$post_id}\\n";

// Update post content to empty string
wp_update_post([
    'ID' => $post_id,
    'post_content' => '',
    'post_excerpt' => 'コンビニで「お弁当温めますか？」と聞かれ、笑顔で元気よく「大丈夫です！」と答えたオスカー。意気揚々とデスクに戻ってフタを開けると……！？ 日本の魔法の言葉「大丈夫」の二面性を描く4コマ漫画！',
    'post_status' => 'publish'
]);

// Regenerate attachment for new image
$upload_dir = wp_upload_dir();
$img_source = get_stylesheet_directory() . '/assets/images/posts/manga-01-daijoubu-trap.jpg';

// Delete existing thumbnail attachment if any
$existing_thumb_id = get_post_thumbnail_id($post_id);
if ($existing_thumb_id) {
    wp_delete_attachment($existing_thumb_id, true);
}

// Copy to uploads
$filename = 'manga-01-daijoubu-trap-' . time() . '.jpg';
$upload_path = $upload_dir['path'] . '/' . $filename;
copy($img_source, $upload_path);

$filetype = wp_check_filetype($filename, null);
$attachment = array(
    'guid'           => $upload_dir['url'] . '/' . $filename, 
    'post_mime_type' => $filetype['type'],
    'post_title'     => 'manga-01-daijoubu-trap',
    'post_content'   => '',
    'post_status'    => 'inherit'
);

$attach_id = wp_insert_attachment($attachment, $upload_path, $post_id);
$attach_data = wp_generate_attachment_metadata($attach_id, $upload_path);
wp_update_attachment_metadata($attach_id, $attach_data);
set_post_thumbnail($post_id, $attach_id);

echo "Successfully updated manga post {$post_id} with new thumbnail {$attach_id} and cleared content!\\n";

if (has_action('litespeed_purge_all')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed cache purged.\\n";
}
"""

with sftp.open('update_manga_post.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php update_manga_post.php && rm update_manga_post.php')
out = stdout.read().decode('utf-8', errors='replace')
print("PHP OUTPUT:\n", out)
err = stderr.read().decode('utf-8', errors='replace')
if err:
    print("PHP STDERR:\n", err)

ssh.close()
print("All updates completed successfully!")
