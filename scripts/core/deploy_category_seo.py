import os
import paramiko
import urllib.request
import re

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
sftp = ssh.open_sftp()

# 1. functions/seo.php をアップロード
remote_seo_path = 'web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/functions/seo.php'
sftp.put('functions/seo.php', remote_seo_path)
print(f"Uploaded: functions/seo.php -> {remote_seo_path}")

# 2. カテゴリーDBのdescription更新 ＆ キャッシュパージ
php_script = r"""<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$cat_updates = [
    'culture-shock' => '香港と日本の文化の違いや生活習慣のギャップに驚いた実体験を徹底解説！真冬の氷水、街中にゴミ箱がない理由、主食×主食の炭水化物コンボ、散髪代5,000円など、外国人視点で発見した日本の面白い日常と文化の深層をお届けします。',
    'comparing' => '似ているけれどニュアンスが全く違う日本語を徹底比較！「全然」VS「全く」、「さようなら」VS「またね」、「あげる」VS「くれる」など、教科書では教えてくれない日常会話のリアルな使い分けを香港出身のオスカーが分かりやすく解説します。',
    'kotoba-no-aya' => '「大丈夫です」「その節はどうも…」「すみません」など、文脈やトーンで意味が180度変わる日本語の「ことばのあや」を深掘り！終助詞「ぞ・ぜ・ね・よ」の微妙なニュアンスや、日本人の本音と建前を外国人視点から分かりやすく解き明かします。',
    'street-japanese' => 'コンビニのレジ、駅の自動改札、居酒屋、美容室、カフェ注文など、教科書には載っていない日本のリアルな日常現場で生き残るための実践的日本語とマナーをRPG風に楽しく攻略する実践サバイバルガイドです。'
];

foreach ($cat_updates as $slug => $desc) {
    $term = get_term_by('slug', $slug, 'category');
    if ($term) {
        wp_update_term($term->term_id, 'category', [
            'description' => $desc
        ]);
        echo "Updated category [{$slug}] (ID: {$term->term_id}) description.\n";
    } else {
        echo "Category [{$slug}] not found!\n";
    }
}

// リライトルールの再フラッシュ
global $wp_rewrite;
$wp_rewrite->set_permalink_structure('/%postname%/');
flush_rewrite_rules(true);

if (function_exists('opcache_reset')) { opcache_reset(); }
if (class_exists('LiteSpeed\\Purge')) { 
    \LiteSpeed\Purge::purge_all(); 
}
do_action('litespeed_purge_all');
wp_cache_flush();

echo "All caches successfully purged!\n";
?>"""

with sftp.open('update_cats_seo.php', 'w') as f:
    f.write(php_script)

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php update_cats_seo.php')
out = stdout.read().decode('utf-8', errors='ignore')
err = stderr.read().decode('utf-8', errors='ignore')
print("REMOTE OUTPUT:\n", out)
if err:
    print("REMOTE ERR:\n", err)

ssh.exec_command('rm update_cats_seo.php')
sftp.close()
ssh.close()
print("Remote DB update and cache purge finished.")
