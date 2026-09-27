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

img_local = "assets/images/posts/manga-01-daijoubu-trap.jpg"
remote_theme_img = "web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/posts/manga-01-daijoubu-trap.jpg"
site_img_url = "https://nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/posts/manga-01-daijoubu-trap.jpg"

gutenberg_content = f"""<!-- wp:image {{"sizeSlug":"full","linkDestination":"none"}} -->
<figure class="wp-block-image size-full"><img src="{site_img_url}" alt="【4コマ漫画】第1話：「大丈夫」はYESなの？NOなの！？" /><figcaption class="wp-element-caption">【4コマ漫画】第1話：「大丈夫」はYESなの？NOなの！？</figcaption></figure>
<!-- /wp:image -->

<!-- wp:heading {{"level":3}} -->
<h3 class="wp-block-heading">📖 各コマのストーリー＆セリフ</h3>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
<li><strong>1コマ目（起）</strong>：🏪 <strong>店員さん</strong>：「<strong>温めますか？</strong>」<br />🚗 <strong>オスカー</strong>：「<strong>大丈夫です！ 😊</strong>」<br />（香港からやってきたオスカー。覚えたての日本語で、コンビニの店員さんに元気よく笑顔で返答！）</li>
<li><strong>2コマ目（承）</strong>：🍱 <strong>オスカー</strong>：「<strong>つめたい……！？ 🥶</strong>」<br />（オフィスに戻ってルンルンで弁当を開けたら、まさかのキンキンに冷えたまま！ 「えっ、大丈夫（温めて問題ないよ）って言ったのに……！？」と青ざめるオスカー）</li>
<li><strong>3コマ目（転）</strong>：☕ <strong>田中先輩</strong>：「<strong>オスカーくん、日本では断るときも『大丈夫』って言うんだよ（笑）</strong>」<br />🚗 <strong>オスカー</strong>：「<strong>わ！？ 英語の No thank you の意味なんですか！？ 😱</strong>」<br />（カフェでコーヒーを飲みながら、優しく日本の暗黙ルールを教えてくれる田中先輩）</li>
<li><strong>4コマ目（結・オチ）</strong>：👥 <strong>別のお客さん</strong>：「<strong>ここ、空いてますか？</strong>」<br />👩‍💼 <strong>カフェ店員</strong>：「<strong>大丈夫ですよ！ どうぞ！</strong>」<br />🚗 <strong>オスカー</strong>：「<strong>今度はYESなのーーー！？ 👻</strong>」<br />（断る言葉だと思ったら、今度は『座ってOK（許可）』のYESの意味で使われて、魂が抜け出るオスカー）</li>
</ul>
<!-- /wp:list -->

<!-- wp:separator -->
<hr class="wp-block-separator has-alpha-channel-opacity" />
<!-- /wp:separator -->

<!-- wp:heading {{"level":3}} -->
<h3 class="wp-block-heading">💡 田中先輩のワンポイント解説</h3>
<!-- /wp:heading -->

<!-- wp:quote -->
<blockquote class="wp-block-quote"><p>「大丈夫です」は、相手の気遣いに対して「（お気遣いなく、現状のままで）問題ありません」というニュアンスから、<strong>「いいえ、結構です（NO）」</strong>の意味で非常によく使われます。<br />でも、許可を求められた時の「大丈夫ですよ」は<strong>「OKです（YES）」</strong>の意味！<br />手振りで軽く手を横に振っていたら「NO」、笑顔で頷いていたら「YES」と見分けるのがコツですよ！</p></blockquote>
<!-- /wp:quote -->"""

b64_content = base64.b64encode(gutenberg_content.encode('utf-8')).decode('ascii')

php_code = f"""<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');
require_once(ABSPATH . 'wp-admin/includes/file.php');
require_once(ABSPATH . 'wp-admin/includes/media.php');

$b64 = '{b64_content}';
$content = base64_decode($b64);

// Check if manga post already exists
$existing = get_posts(array(
    'post_type' => 'manga',
    'name' => 'manga-01-daijoubu-trap',
    'post_status' => 'any',
    'numberposts' => 1
));

$post_data = array(
    'post_title'   => '【4コマ漫画】第1話：「大丈夫」はYESなの？NOなの！？｜コンビニ温めトラップ',
    'post_name'    => 'manga-01-daijoubu-trap',
    'post_type'    => 'manga',
    'post_status'  => 'publish',
    'post_content' => $content,
    'post_date'    => '2026-09-11 09:00:00',
    'meta_input'   => array(
        'connected_post_id' => 172
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

// Set category
$cat = get_category_by_slug('kotoba-no-aya');
if ($cat) {{
    wp_set_post_categories($post_id, array($cat->term_id));
}}

// Upload image to media library and set as featured image
$remote_img_path = getenv('HOME') . '/{remote_theme_img}';
if (file_exists($remote_img_path)) {{
    $file_array = array(
        'name'     => basename($remote_img_path),
        'tmp_name' => $remote_img_path
    );
    // Check if attachment already exists
    global $wpdb;
    $attach_id = $wpdb->get_var($wpdb->prepare("SELECT ID FROM $wpdb->posts WHERE post_title = %s AND post_type = 'attachment'", 'manga-01-daijoubu-trap'));
    
    if (!$attach_id) {{
        $attach_id = media_handle_sideload($file_array, $post_id, '【4コマ漫画】第1話：「大丈夫」はYESなの？NOなの！？');
    }}
    if (!is_wp_error($attach_id)) {{
        set_post_thumbnail($post_id, $attach_id);
        echo "Set featured image attachment ID: " . $attach_id . PHP_EOL;
    }} else {{
        echo "Media sideload note: " . $attach_id->get_error_message() . PHP_EOL;
    }}
}}

$url = get_permalink($post_id);
echo "Manga URL: " . $url . PHP_EOL;

if (has_action('litespeed_purge_all')) {{
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache Purged All!" . PHP_EOL;
}}
"""

max_retries = 6
for attempt in range(1, max_retries + 1):
    try:
        print(f"Connecting to SSH (Attempt {attempt}/{max_retries})...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], timeout=10)
        sftp = ssh.open_sftp()
        print("Connected!")

        # Upload image to theme assets
        print(f"Uploading image to {remote_theme_img}...")
        sftp.put(img_local, remote_theme_img)
        print("Image uploaded successfully!")

        # Write PHP script
        with sftp.open('post_manga_daijoubu.php', 'w') as f:
            f.write(php_code)

        print("Executing post creation script...")
        stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php post_manga_daijoubu.php && rm post_manga_daijoubu.php')
        out = stdout.read().decode('utf-8', errors='replace')
        print(out)
        err = stderr.read().decode('utf-8', errors='replace')
        if err:
            print("Stderr:", err)

        sftp.close()
        ssh.close()
        print("Finished!")
        break
    except Exception as e:
        print(f"Attempt {attempt} failed: {e}")
        if attempt < max_retries:
            print("Waiting 15 seconds before retry...")
            time.sleep(15)
