import os
import re
import sys
import base64
import time
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

def publish_manga():
    img_local = "assets/images/posts/manga-01-shouchidesu.jpg"
    theme_remote_img = "web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/posts/manga-01-shouchidesu.jpg"
    site_img_url = "https://nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/posts/manga-01-shouchidesu.jpg"

    # Gutenberg content
    gutenberg_content = f"""<!-- wp:image {{"sizeSlug":"full","linkDestination":"none"}} -->
<figure class="wp-block-image size-full"><img src="{site_img_url}" alt="【4コマ漫画】第1話：「承知です」はダメですか！？" /><figcaption class="wp-element-caption">【4コマ漫画】第1話：「承知です」はダメですか！？</figcaption></figure>
<!-- /wp:image -->

<!-- wp:heading {{"level":3}} -->
<h3 class="wp-block-heading">📖 各コマのストーリー＆セリフ</h3>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
<li><strong>1コマ目</strong>：💻 <strong>オスカー</strong>：「<strong>承知です！（shouchi desu!）</strong>」<br />（先輩からの指示チャットに、元気いっぱいの笑顔でタイピングするオスカー）</li>
<li><strong>2コマ目</strong>：✉️ <strong>オスカー</strong>：「<strong>送信！ enter</strong>」<br />（「了解です」は失礼だと知っているオスカー。「承知」に変えた自分に大満足でEnterキーをッターン！）</li>
<li><strong>3コマ目</strong>：👔 <strong>田中先輩</strong>：「<strong>オスカーさん、ビジネスでは『承知いたしました』がもっと丁寧ですよ。気をつけて。（苦笑）</strong>」<br />（そっと後ろから肩に手を置き、優しく耳打ちする田中先輩）</li>
<li><strong>4コマ目</strong>：👻 <strong>オスカー</strong>：「<strong>えっ？！ もっと丁寧な表現が…！？ なるほど！『承知いたしました』！</strong>」<br />（魂が口から抜け出ながらも、新しい日本語をインプットして前向きに納得するオスカー）</li>
</ul>
<!-- /wp:list -->

<!-- wp:separator -->
<hr class="wp-block-separator has-alpha-channel-opacity" />
<!-- /wp:separator -->

<!-- wp:heading {{"level":3}} -->
<h3 class="wp-block-heading">💡 田中先輩のオフィス敬語ワンポイントメモ</h3>
<!-- /wp:heading -->

<!-- wp:quote -->
<blockquote class="wp-block-quote"><p>「承知」はそれ自体が相手を敬う言葉ですが、「です」をつけると少し雑な省略形に聞こえてしまいます。<br />ビジネスチャットや目上の上司に対しては、語尾も謙譲語で揃えて<strong>「承知いたしました」</strong>、または社内なら<strong>「承知しました」</strong>と返すのがスマートですよ！</p></blockquote>
<!-- /wp:quote -->"""

    b64_content = base64.b64encode(gutenberg_content.encode('utf-8')).decode('ascii')

    php_code = f"""<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$b64 = '{b64_content}';
$content = base64_decode($b64);

// Check if manga post already exists
$existing = get_posts(array(
    'post_type' => 'manga',
    'name' => 'manga-01-shouchidesu',
    'post_status' => 'any',
    'numberposts' => 1
));

$post_data = array(
    'post_title'   => '【4コマ漫画】第1話：「承知です」はダメですか！？｜オフィス敬語の落とし穴',
    'post_name'    => 'manga-01-shouchidesu',
    'post_type'    => 'manga',
    'post_status'  => 'publish',
    'post_content' => $content,
    'post_date'    => '2026-10-13 09:00:00',
    'meta_input'   => array(
        'connected_post_id' => 2472
    )
);

if (!empty($existing)) {{
    $post_data['ID'] = $existing[0]->ID;
    $post_id = wp_update_post($post_data);
    echo "[UPDATED Manga Post ID: " . $post_id . "]" . PHP_EOL;
}} else {{
    $post_id = wp_insert_post($post_data);
    echo "[CREATED Manga Post ID: " . $post_id . "]" . PHP_EOL;
}}

// Set category if exists
$cat = get_category_by_slug('kotoba-no-aya');
if ($cat) {{
    wp_set_post_categories($post_id, array($cat->term_id));
}}

$url = get_permalink($post_id);
echo "Manga URL: " . $url . PHP_EOL;

if (has_action('litespeed_purge_all')) {{
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache Purged All!" . PHP_EOL;
}}
"""

    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Connecting to SSH (Attempt {attempt}/{max_retries})...")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], timeout=10)
            sftp = ssh.open_sftp()

            # Upload image
            print(f"Uploading image to {theme_remote_img}...")
            sftp.put(img_local, theme_remote_img)
            print("Image uploaded successfully!")

            # Write and execute PHP script
            with sftp.open('publish_manga_script.php', 'w') as f:
                f.write(php_code)

            stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php publish_manga_script.php && rm publish_manga_script.php')
            out = stdout.read().decode('utf-8', errors='replace')
            print(out)

            sftp.close()
            ssh.close()
            print("Manga post published successfully!")
            return True
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                print("Waiting 15 seconds before retry...")
                time.sleep(15)

    return False

if __name__ == '__main__':
    publish_manga()
