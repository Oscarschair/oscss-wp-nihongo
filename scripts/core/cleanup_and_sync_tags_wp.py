import os
import sys
import json
import paramiko

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from update_markdown_tags import TAG_MAPPING

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

theme_dir = "web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo"
remote_json = f"{theme_dir}/tags_sync_payload.json"
remote_php = f"{theme_dir}/cleanup_tags.php"

payload = {
    "mapping": TAG_MAPPING
}

with sftp.file(remote_json, 'w') as f:
    json.dump(payload, f, ensure_ascii=False)

php_script = """<?php
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
global $wpdb;

$json_path = getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/tags_sync_payload.json';
$data = json_decode(file_get_contents($json_path), true);
$mapping = $data['mapping'];

echo "--- 全投稿のタグを確実に新体系に同期 ---\\n";
$updated_posts = 0;
foreach ($mapping as $slug => $tags) {
    $post_id = $wpdb->get_var($wpdb->prepare("SELECT ID FROM {$wpdb->posts} WHERE post_name = %s AND post_type = 'post'", $slug));
    if ($post_id) {
        wp_set_post_tags((int)$post_id, $tags, false);
        clean_post_cache((int)$post_id);
        $updated_posts++;
        echo "Post ID " . $post_id . " (" . $slug . ") => " . implode(', ', $tags) . "\\n";
    } else {
        echo "Post still not found for slug: " . $slug . "\\n";
    }
}
echo "Total updated posts: " . $updated_posts . " / " . count($mapping) . "\\n\\n";

// タグ使用件数の再集計
wp_update_term_count_now(get_terms(array('taxonomy' => 'post_tag', 'fields' => 'ids', 'hide_empty' => false)), 'post_tag');

$current_tags = get_terms(array(
    'taxonomy' => 'post_tag',
    'hide_empty' => false,
));

echo "--- 現在のWordPressタグ一覧 (計 " . count($current_tags) . " 個) ---\\n";
foreach ($current_tags as $t) {
    echo "- " . $t->name . " (件数: " . $t->count . ")\\n";
}

// OPcache, LiteSpeed, Object Cache パージ
if (function_exists('opcache_reset')) { opcache_reset(); }
if (class_exists('LiteSpeed\\\\Purge')) { 
    \\LiteSpeed\\Purge::purge_all(); 
}
do_action('litespeed_purge_all');
wp_cache_flush();
echo "\\nAll caches purged successfully!\\n";
?>"""

with sftp.file(remote_php, 'w') as f:
    f.write(php_script)

print("Executing precise tag synchronization on remote server...")
stdin, stdout, stderr = ssh.exec_command(f'LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php $HOME/{remote_php} && rm -f $HOME/{remote_php} $HOME/{remote_json}')
out = stdout.read().decode('utf-8', errors='ignore')
err = stderr.read().decode('utf-8', errors='ignore')

print("OUTPUT:\n", out)
if err:
    print("ERR:\n", err)

sftp.close()
ssh.close()
