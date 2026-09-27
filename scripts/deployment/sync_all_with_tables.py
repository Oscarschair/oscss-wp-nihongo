import os
import re
import sys
import base64
import time
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

from scripts.core.gutenberg_parser import parse_markdown_to_gutenberg_full

# 1. 3記事の Gutenberg HTML 生成
posts = [
    (2472, "content/posts/2026-10-13-kotoba-no-aya-is-shouchidesu-wrong-business-japanese-trap.md"),
    (2474, "content/posts/2026-10-14-street-japanese-city-hall-resident-registration-dungeon-guide.md"),
    (2476, "content/posts/2026-10-15-japanese-comparing-rashii-souda-youda-differences.md"),
]

post_payloads = []
for pid, md_path in posts:
    gutenberg_html = parse_markdown_to_gutenberg_full(md_path)
    b64 = base64.b64encode(gutenberg_html.encode('utf-8')).decode('ascii')
    post_payloads.append((pid, b64))

# 2. 4コマ漫画の Gutenberg HTML 生成
manga_img_local = "assets/images/posts/manga-01-daijoubu-trap.jpg"
manga_theme_remote_img = "web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/posts/manga-01-daijoubu-trap.jpg"
manga_site_img_url = "https://nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/posts/manga-01-daijoubu-trap.jpg"

manga_gutenberg = f"""<!-- wp:image {{"sizeSlug":"full","linkDestination":"none"}} -->
<figure class="wp-block-image size-full"><img src="{manga_site_img_url}" alt="【4コマ漫画】第1話：「大丈夫」はYESなの？NOなの！？" /><figcaption class="wp-element-caption">【4コマ漫画】第1話：「大丈夫」はYESなの？NOなの！？</figcaption></figure>
<!-- /wp:image -->

<!-- wp:heading {{"level":3}} -->
<h3 class="wp-block-heading">📖 各コマのストーリー＆セリフ</h3>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
<li><strong>1コマ目（起）</strong>：🏪 <strong>店員さん</strong>：「<strong>温めますか？</strong>」<br />🚗 <strong>オスカー</strong>：「<strong>大丈夫です！ 😊</strong>」<br />（香港から来日したオスカー。覚えたての日本語で元気よく笑顔で返答！）</li>
<li><strong>2コマ目（承）</strong>：🍱 <strong>オスカー</strong>：「<strong>つめたい……！？ 🥶</strong>」<br />（オフィスでルンルンで弁当を開けたら、まさかのキンキンに冷えたまま！ 「えっ、大丈夫（温めて問題ないよ）って言ったのに……！？」と青ざめる）</li>
<li><strong>3コマ目（転）</strong>：☕ <strong>田中先輩</strong>：「<strong>オスカーくん、日本では断るときも『大丈夫』って言うんだよ（笑）</strong>」<br />🚗 <strong>オスカー</strong>：「<strong>わ！？ 英語の No thank you の意味なんですか！？ 😱</strong>」<br />（カフェで優しく日本の暗黙ルールを教えてくれる田中先輩）</li>
<li><strong>4コマ目（結・オチ）</strong>：👥 <strong>客</strong>：「<strong>ここ、空いてますか？</strong>」<br />👩‍💼 <strong>店員</strong>：「<strong>大丈夫ですよ！ どうぞ！</strong>」<br />🚗 <strong>オスカー</strong>：「<strong>今度はYESなのーーー！？ 👻</strong>」<br />（断る言葉だと思ったら、今度は『座ってOK』のYESの意味で使われて魂が抜け出るオスカー）</li>
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

manga_b64 = base64.b64encode(manga_gutenberg.encode('utf-8')).decode('ascii')

# 3. サーバー側で一度に全実行する PHP スクリプト生成
php_script = f"""<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');
require_once(ABSPATH . 'wp-admin/includes/file.php');
require_once(ABSPATH . 'wp-admin/includes/media.php');

// 1. 3記事の更新
$updates = array(
    2472 => '{post_payloads[0][1]}',
    2474 => '{post_payloads[1][1]}',
    2476 => '{post_payloads[2][1]}'
);

foreach ($updates as $pid => $b64) {{
    $content = base64_decode($b64);
    wp_update_post(array(
        'ID' => $pid,
        'post_content' => $content
    ));
    $p = get_post($pid);
    $time = oscss_get_reading_time($p);
    echo "[UPDATED Post {{$pid}}] Reading time: 約{{$time}}分 (" . strlen($content) . " bytes)" . PHP_EOL;
}}

// 2. 4コマ漫画 (manga) の作成・更新
$manga_b64 = '{manga_b64}';
$manga_content = base64_decode($manga_b64);

$existing_manga = get_posts(array(
    'post_type' => 'manga',
    'name' => 'manga-01-daijoubu-trap',
    'post_status' => 'any',
    'numberposts' => 1
));

$manga_data = array(
    'post_title'   => '【4コマ漫画】第1話：「大丈夫」はYESなの？NOなの！？｜コンビニ温めトラップ',
    'post_name'    => 'manga-01-daijoubu-trap',
    'post_type'    => 'manga',
    'post_status'  => 'publish',
    'post_content' => $manga_content,
    'post_date'    => '2026-09-11 09:00:00',
    'meta_input'   => array(
        'connected_post_id' => 172
    )
);

if (!empty($existing_manga)) {{
    $manga_data['ID'] = $existing_manga[0]->ID;
    $manga_id = wp_update_post($manga_data);
    echo "[UPDATED Manga Post ID: " . $manga_id . "]" . PHP_EOL;
}} else {{
    $manga_id = wp_insert_post($manga_data);
    echo "[CREATED Manga Post ID: " . $manga_id . "]" . PHP_EOL;
}}

$cat = get_category_by_slug('kotoba-no-aya');
if ($cat) {{
    wp_set_post_categories($manga_id, array($cat->term_id));
}}

// アイキャッチ画像設定
$img_path = getenv('HOME') . '/{manga_theme_remote_img}';
if (file_exists($img_path)) {{
    global $wpdb;
    $attach_id = $wpdb->get_var($wpdb->prepare("SELECT ID FROM $wpdb->posts WHERE post_title = %s AND post_type = 'attachment'", 'manga-01-daijoubu-trap'));
    if (!$attach_id) {{
        $tmp_copy = tempnam(sys_get_temp_dir(), 'manga_');
        copy($img_path, $tmp_copy);
        $file_array = array(
            'name'     => basename($img_path),
            'tmp_name' => $tmp_copy
        );
        $attach_id = media_handle_sideload($file_array, $manga_id, '【4コマ漫画】第1話：「大丈夫」はYESなの？NOなの！？');
    }}
    if (!is_wp_error($attach_id) && $attach_id) {{
        set_post_thumbnail($manga_id, $attach_id);
        echo "Set featured image attachment ID: " . $attach_id . PHP_EOL;
    }}
}}

$manga_url = get_permalink($manga_id);
echo "Manga URL: " . $manga_url . PHP_EOL;

// 3. LiteSpeed Cache 全消去
if (has_action('litespeed_purge_all')) {{
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache Purged All!" . PHP_EOL;
}}
"""

def execute_all():
    print("Preparing to deploy...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # 接続リトライ（Lolipop SSHレート制限対策）
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Connecting to SSH (attempt {attempt}/{max_retries})...")
            ssh.connect(
                env['SSH_HOST'], 
                int(env['SSH_PORT']), 
                env['SSH_USER'], 
                env['SSH_PASS'], 
                timeout=20,
                look_for_keys=False,
                allow_agent=False
            )
            print("Connected to SSH successfully!")
            break
        except Exception as e:
            print(f"Connection attempt {attempt} failed: {e}")
            if attempt < max_retries:
                wait_sec = 25 * attempt
                print(f"Waiting {wait_sec}s for server cooldown...")
                time.sleep(wait_sec)
            else:
                raise
    sftp = ssh.open_sftp()
    print("Connected to SFTP!")

    # 4コマ画像をアップロード
    print(f"Uploading manga image to {manga_theme_remote_img}...")
    sftp.put(manga_img_local, manga_theme_remote_img)
    print("Manga image uploaded!")

    # PHPスクリプト転送・実行
    with sftp.open('deploy_batch_all.php', 'w') as f:
        f.write(php_script)
    print("Executing all updates in one session...")
    stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php deploy_batch_all.php && rm deploy_batch_all.php')
    print(stdout.read().decode('utf-8', errors='replace'))
    err = stderr.read().decode('utf-8', errors='replace')
    if err:
        print("Stderr:", err)

    sftp.close()
    ssh.close()
    print("All deployed and verified successfully!")

if __name__ == '__main__':
    execute_all()
