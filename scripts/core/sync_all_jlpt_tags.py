import glob
import re
import os
import json
import paramiko

# 1. 未設定だった過去10記事のJLPTレベル定義
EXTRA_JLPT = {
    "japanese-comparing-sorry-excuse-me-differences-in-apology-expressions": "N4〜N3",
    "kotoba-no-aya-how-to-use-the-final-particle-ne-for-a-comfortable-conversation": "N4〜N3",
    "japanese-comparing-interesting-and-oddy-funny-differences-in-emotional-expression": "N3",
    "japanese-comparing-scholarships-in-japan-and-overseas-different-meaning-with-same-word": "N2",
    "kotoba-no-aya-how-to-use-the-final-particle-yo-for-effective-conversation": "N4〜N3",
    "culture-shock-ice-water-hospitality-in-winter-vs-hot-water-culture": "N3",
    "culture-shock-sleeping-on-the-train-japan-safety-and-inemuri-culture": "N3",
    "kotoba-no-aya-how-to-distinguish-yes-and-no-in-iidesu": "N3",
    "kotoba-no-aya-how-to-use-the-final-particle-yone-for-smooth-conversation": "N4〜N3",
    "japanese-comparing-wakaru-and-shiru-differences-in-understanding-and-knowing": "N4〜N3",
}

# 全記事を走査して jlpt フィールドを補完し、tags に JLPT タグを追加
post_updates = {}
total_files = 0
for f in sorted(glob.glob('content/posts/*.md')):
    content = open(f, encoding='utf-8').read()
    fm_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        continue
    fm = fm_match.group(1)
    slug_match = re.search(r'slug:\s*["\']?([^"\']+)["\']?', fm)
    if not slug_match:
        continue
    slug = slug_match.group(1).strip()
    total_files += 1

    # 1. jlpt レベルの取得または補完
    jlpt_match = re.search(r'jlpt:\s*["\']?([^"\']+)["\']?', fm)
    if jlpt_match:
        jlpt_val = jlpt_match.group(1).strip()
    else:
        jlpt_val = EXTRA_JLPT.get(slug, "N3")
        # fm に追加
        fm = fm + f'\njlpt: "{jlpt_val}"\n'

    # 2. JLPTタグの生成
    jlpt_tags = []
    if "N4" in jlpt_val:
        jlpt_tags.append("JLPT N4")
    if "N3" in jlpt_val:
        jlpt_tags.append("JLPT N3")
    if "N2" in jlpt_val:
        jlpt_tags.append("JLPT N2")
    if "N1" in jlpt_val:
        jlpt_tags.append("JLPT N1")
    if not jlpt_tags:
        jlpt_tags.append("JLPT")

    # 3. 既存 tags ブロックの取得とマージ
    tag_block = re.search(r'tags:\s*\n((?:\s*-\s*[^\n]+\n?)+)', fm)
    cur_tags = []
    if tag_block:
        cur_tags = [re.sub(r'["\']', '', l.replace('-', '').strip()) for l in tag_block.group(1).strip().split('\n') if l.strip()]

    # 重複なしで結合
    merged_tags = []
    for t in cur_tags:
        if t not in merged_tags and not t.startswith("JLPT"):
            merged_tags.append(t)
    for jt in jlpt_tags:
        if jt not in merged_tags:
            merged_tags.append(jt)

    new_tag_block = "tags:\n" + "\n".join([f"  - {t}" for t in merged_tags])
    if tag_block:
        new_fm = re.sub(r'tags:\s*\n(?:\s*-\s*[^\n]+\n?)+', new_tag_block + "\n", fm)
    else:
        new_fm = fm + "\n" + new_tag_block + "\n"

    new_content = re.sub(r'^---\s*\n.*?\n---', f"---\n{new_fm.strip()}\n---", content, flags=re.DOTALL)
    with open(f, 'w', encoding='utf-8') as out_f:
        out_f.write(new_content)

    post_updates[slug] = {
        "jlpt": jlpt_val,
        "tags": merged_tags
    }

print(f"Processed {len(post_updates)} / {total_files} markdown posts.")

# 4. WordPress DB に SSH 経由で一括反映
env_data = {}
with open('.env.deploy', 'r', encoding='utf-8') as ef:
    for line in ef:
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
remote_json = f"{theme_dir}/all_jlpt_tags_payload.json"
remote_php = f"{theme_dir}/sync_jlpt_tags.php"

with sftp.file(remote_json, 'w') as f:
    json.dump(post_updates, f, ensure_ascii=False)

php_script = """<?php
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
global $wpdb;

$json_path = getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/all_jlpt_tags_payload.json';
$data = json_decode(file_get_contents($json_path), true);

$updated_count = 0;
foreach ($data as $slug => $info) {
    $post_id = $wpdb->get_var($wpdb->prepare("SELECT ID FROM {$wpdb->posts} WHERE post_name = %s AND post_type = 'post'", $slug));
    if ($post_id) {
        // 1. タグの上書き設定
        wp_set_post_tags((int)$post_id, $info['tags'], false);
        // 2. JLPTレベルメタの保存
        update_post_meta((int)$post_id, '_oscss_jlpt_level', $info['jlpt']);
        clean_post_cache((int)$post_id);
        $updated_count++;
        echo "Post ID " . $post_id . " (" . $slug . ") => JLPT: " . $info['jlpt'] . ", Tags: " . implode(', ', $info['tags']) . "\\n";
    } else {
        echo "Post not found for slug: " . $slug . "\\n";
    }
}
echo "Total updated posts: " . $updated_count . " / " . count($data) . "\\n";

// タグ使用件数再集計
wp_update_term_count_now(get_terms(array('taxonomy' => 'post_tag', 'fields' => 'ids', 'hide_empty' => false)), 'post_tag');

// キャッシュパージ
if (function_exists('opcache_reset')) { opcache_reset(); }
if (class_exists('LiteSpeed\\\\Purge')) { 
    \\LiteSpeed\\Purge::purge_all(); 
}
do_action('litespeed_purge_all');
wp_cache_flush();
echo "All caches purged successfully!\\n";
?>"""

with sftp.file(remote_php, 'w') as f:
    f.write(php_script)

print("Synchronizing all JLPT tags and meta to WordPress...")
stdin, stdout, stderr = ssh.exec_command(f'LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php $HOME/{remote_php} && rm -f $HOME/{remote_php} $HOME/{remote_json}')
out = stdout.read().decode('utf-8', errors='ignore')
err = stderr.read().decode('utf-8', errors='ignore')

print("OUTPUT:\n", out)
if err:
    print("ERR:\n", err)

sftp.close()
ssh.close()
print("JLPT tags synchronization completed.")
