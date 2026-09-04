import json
import paramiko

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
deploy_dir = env_data.get('DEPLOY_DIR', '~/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/').replace('~/', '')

# 吹き出しブロック生成ヘルパー
def make_balloon(speaker_name, avatar_url, position, paragraphs):
    p_html = "".join([f"<!-- wp:paragraph -->\n<p>{p}</p>\n<!-- /wp:paragraph -->\n" for p in paragraphs])
    pos_class = "sbp-l" if position == "l" else "sbp-r"
    return f"""<!-- wp:cocoon-blocks/balloon-ex-box-1 {{"name":"{speaker_name}","icon":"{avatar_url}","position":"{position}"}} -->
<div class="wp-block-cocoon-blocks-balloon-ex-box-1 speech-wrap sb-id-1 sbs-stn {pos_class} sbis-cb cf block-box"><div class="speech-person"><figure class="speech-icon"><img src="{avatar_url}" alt="{speaker_name}" class="speech-icon-image"/></figure><div class="speech-name">{speaker_name}</div></div><div class="speech-balloon">{p_html}</div></div>
<!-- /wp:cocoon-blocks/balloon-ex-box-1 -->"""

oscar_avatar = "http://nihongo.oscarchair.jp/wp-content/uploads/2023/02/my-icon1.jpg"
man_avatar = "http://nihongo.oscarchair.jp/wp-content/themes/cocoon-master/images/man.png"
woman_avatar = "http://nihongo.oscarchair.jp/wp-content/themes/cocoon-master/images/woman.png"

# 記事データ
new_posts = [
    {
        "title": "カルチャーショック：真冬でも氷水！？日本の「冷たいおもてなし」と中華圏の「温かいお湯」文化",
        "slug": "culture-shock-ice-water-hospitality-in-winter-vs-hot-water-culture",
        "category_slug": "culture-shock",
        "category_name": "カルチャーショック",
        "thumb_file": "thumb-culture-ice-water.jpg",
        "content": f"""{make_balloon('オスカー', oscar_avatar, 'l', [
            'こんにちは、オスカーです。',
            '今回は、日本の飲食店で誰もが一度は体験する「お冷（おひや）」にまつわるカルチャーショックをご紹介します。',
            '日本に来たばかりの頃、外の気温が0度近い真冬の日にレストランに入ったのですが、席に着くなりグラスいっぱいのキンキンに冷えた「氷水」を出されて思わず固まってしまいました…！',
            '今回は、日本と中華圏における「水・お茶」に対する価値観の大きな違いと、その面白い歴史的背景についてお話しします。'
        ])}

<!-- wp:heading -->
<h2>中華圏の常識：「冷たい飲み物」は体に毒！？</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>まず、香港や中国・台湾などの中華圏における基本的な常識をお話しします。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>中華圏では、季節を問わず<strong>「温かいお茶」や「白湯（さゆ・温かいお湯）」を飲むのが当たり前</strong>です。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>これは長い歴史を持つ中医学（漢方・東洋医学）の「養生（体をいたわる）」という思想が、日常の食習慣に深く根付いているためです。</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li><strong>体を冷やすと万病の元になる</strong></li>
<li><strong>冷たい水は内臓を冷やし、消化や血流を悪くする</strong></li>
<li><strong>常にお腹を温めておくことが健康・長寿の秘訣</strong></li>
</ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>このように幼い頃から教えられて育つため、中華圏のレストランでは真夏であっても基本的に温かいお茶か常温の水が提供されます。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>もし真冬の香港のレストランで氷水を出されたら、お客さんは「えっ、何か嫌がらせされているの…？」と本気で驚いてしまうレベルです（笑）。</p>
<!-- /wp:paragraph -->

{make_balloon('日本の友人', woman_avatar, 'r', [
    'ええっ！？ 真夏でも温かいお茶を飲むの？ 日本だと「冷たいお冷」が出てくるのが当たり前すぎて、疑問にすら思わなかったよ！'
])}

<!-- wp:heading -->
<h2>なぜ日本では真冬でも「氷水」を出すのか？</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>では、なぜ日本の飲食店では、真冬であっても当たり前のように氷水が無料で提供されるのでしょうか？</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>不思議に思って調べてみたところ、そこには日本ならではの<strong>深い「おもてなしの歴史」</strong>がありました。</p>
<!-- /wp:paragraph -->

<!-- wp:heading {{"level":3}} -->
<h3>1. 「氷水」が貴重な高級品だった時代のおもてなし</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>かつて冷蔵庫や製氷機がなかった江戸〜明治時代、天然の氷は冬場に切り出して「氷室（ひむろ）」に保管しておく超高級品でした。<br>そのため、大切なお客様を迎える際に「わざわざ貴重な氷で冷やした水」を差し出すことは、<strong>最大級の敬意と真心を示す贅沢なおもてなし</strong>だったのです。その文化が、現代の飲食業界にも「お冷サービス」として受け継がれています。</p>
<!-- /wp:paragraph -->

<!-- wp:heading {{"level":3}} -->
<h3>2. 世界有数の「水道水の安全性と美味しさ」への信頼</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>世界的に見ても、水道水をそのまま安心してゴクゴク飲める国はごくわずかです。<br>日本は水源が豊かで水質管理が極めて高いため、「冷やすだけで最高に美味しい飲み物になる」という水への絶対的な信頼と誇りがあるからこそ、定番のおもてなしとして定着したと言えます。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>「思いやり」のアプローチが正反対で面白い！</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>比較してみると、両者の根底にあるのはどちらも<strong>「相手に対する思いやり（ホスピタリティ）」</strong>であることが分かります。</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li><strong>中華圏のおもてなし</strong>：「相手の体を冷やさず、健康を気遣う」ために温かいお茶を出す</li>
<li><strong>日本のおもてなし</strong>：「清らかで美味しい贅沢な水で、喉を潤してもらう」ために冷たいお冷を出す</li>
</ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>目指している「優しさ」は同じなのに、文化や歴史の違いによって真逆の形で表現されているのが本当に興味深いですね。</p>
<!-- /wp:paragraph -->

{make_balloon('オスカー', oscar_avatar, 'l', [
    '（※ちなみに猫舌のオスカーは、日本で生活するうちに、ラーメンやカレーの後に飲むキリッと冷えたお冷の美味しさにすっかり魅了されてしまいました！）'
])}

<!-- wp:heading -->
<h2>おわりに</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>日常の中で何気なく出される一杯のお冷にも、日本が誇る歴史とおもてなしの心が詰まっています。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>街の定食屋さんやレストランでお水を飲むとき、こうした文化の違いを少し思い出してみると、いつもの食事がもっと楽しく味わえるかもしれません。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>今日も最後まで読んでいただき、ありがとうございました。<br>お役に立てれば幸いです。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>それでは！</p>
<!-- /wp:paragraph -->"""
    },
    {
        "title": "カルチャーショック：電車で全員が寝ている！？日本の「居眠り文化」と圧倒的な治安の良さ",
        "slug": "culture-shock-sleeping-on-the-train-japan-safety-and-inemuri-culture",
        "category_slug": "culture-shock",
        "category_name": "カルチャーショック",
        "thumb_file": "thumb-culture-train-sleep.jpg",
        "content": f"""{make_balloon('オスカー', oscar_avatar, 'l', [
            'こんにちは、オスカーです。',
            '今回は、日本を訪れた外国人がほぼ100%驚愕する日本の日常風景――「電車の居眠り」についてのカルチャーショックをご紹介します。',
            '初めて日本の通勤電車に乗った日、座席に座っている人の多くが目を閉じてぐっすり眠り、中にはスマートフォンを手に握ったまま爆睡している人まで見かけて、「ここは天国か！？」「誰もスリを警戒しないの！？」と強烈な衝撃を受けました。',
            '今回は、なぜ日本人は電車でここまで無防備に眠れるのか、その背景にある治安と独自の文化についてお話しします。'
        ])}

<!-- wp:heading -->
<h2>海外の常識：電車で寝るのは「どうぞ盗んでください」のサイン</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>まず、香港や欧米諸国をはじめとする海外の都市部では、公共交通機関で寝ることは<strong>「極めて危険な行為（絶対NG）」</strong>とされています。</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li><strong>居眠りはスリや置き引きの格好のターゲットになる</strong></li>
<li><strong>バッグは胸の前に抱え込み、ファスナーに手を添えて警戒するのが鉄則</strong></li>
<li><strong>常に周囲の人の動きに気を配りながら乗車する</strong></li>
</ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>これが世界の多くの国における当たり前の自衛意識です。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>そのため、海外から日本に来た旅行者が、電車内で完全に脱力して眠りこけている乗客たちを見ると、「信じられない！」「防犯意識がゼロなのでは！？」とカルチャーショックを受けることになります。</p>
<!-- /wp:paragraph -->

{make_balloon('日本の友人', man_avatar, 'r', [
    'ええっ！ 電車でうたた寝するのってそんなに危険なの？ 日本人にとっては、通勤中の電車は一番落ち着いて眠れる場所かも（笑）。'
])}

<!-- wp:heading -->
<h2>なぜ日本人は電車の中で熟睡できるのか？</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>では、なぜ日本の電車内ではこれほど平和に眠ることができるのでしょうか？<br>そこには、日本の社会が生み出した3つの大きな要因があります。</p>
<!-- /wp:paragraph -->

<!-- wp:heading {{"level":3}} -->
<h3>1. 圧倒的な治安の良さと「他人の物を盗まない」高いモラル</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>日本は世界でもトップクラスに犯罪率が低く、「落とし物がそのまま戻ってくる国」としても有名です。<br>「周りの乗客が自分の荷物を盗むはずがない」という社会全体の高い相互信頼があるからこそ、人は無意識にリラックスして眠りに落ちることができます。</p>
<!-- /wp:paragraph -->

<!-- wp:heading {{"level":3}} -->
<h3>2. 世界で注目される日本独自の「居眠り（Inemuri）」文化</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>海外では公の場で寝ることは「怠惰・不真面目」と見なされがちですが、日本では職場や移動中の居眠りは<strong>「それだけ限界まで一生懸命働いた証拠」</strong>として寛容に受け止められる独特の文化的土壌があります。<br>実は英語圏でも「Inemuri」という日本語のまま学術研究されるほど、日本特有の興味深い社会現象として知られています。</p>
<!-- /wp:paragraph -->

<!-- wp:heading {{"level":3}} -->
<h3>3. 日本の電車の快適さ（正確性・静寂・心地よい揺れ）</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>時刻表通りに寸分違わず運行し、車内が極めて清潔で、乗客全員が静かに過ごすマナーを守っている――。<br>この「究極の安心空間」と電車の規則正しい揺れが、心地よい眠りを誘う最高の環境を作り出しています。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>外国人がさらに驚く「目的駅でピタッと起きる特殊能力」</h2>
<!-- /wp:heading -->

{make_balloon('オスカー', oscar_avatar, 'l', [
    'ちなみに、私が居眠り文化と同じくらい驚いたのは、日本人通勤客の「超人的な体内時計」です。'
])}

<!-- wp:paragraph -->
<p>さっきまで完全に白目をむいて爆睡していた人が、自分の降りる駅に電車が滑り込んだ瞬間にスッと目を覚まし、何事もなかったかのようにスマートにホームへ降りていく姿を何度も目撃しました。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>「一体どういうセンサーがついているんだ…！？」と今でも不思議でたまりません（笑）。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>おわりに</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>電車の中で誰もが安心して眠れるというのは、決して当たり前のことではなく、日本の治安の良さ、人々の高いマナー、そして社会の平和が築き上げた<strong>「世界に誇るべき奇跡のような光景」</strong>です。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>毎日の通勤電車でウトウトできる日本の日常の平和に、改めて感謝したくなるカルチャーショックでした。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>今日も最後まで読んでいただき、ありがとうございました。<br>お役に立てれば幸いです。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>それでは！</p>
<!-- /wp:paragraph -->"""
    }
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=host, port=port, username=user, password=password, look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

# 1. サムネイル画像のアップロード
remote_thumbs_dir = f'{deploy_dir.rstrip("/")}/assets/images/thumbnails'
for p in new_posts:
    local_thumb = f'assets/images/thumbnails/{p["thumb_file"]}'
    remote_thumb = f'{remote_thumbs_dir}/{p["thumb_file"]}'
    print(f"Uploading {local_thumb} -> {remote_thumb}...")
    sftp.put(local_thumb, remote_thumb)

# 2. JSONデータ作成
with sftp.open('new_posts_payload.json', 'w') as f:
    f.write(json.dumps(new_posts, ensure_ascii=False))

# 3. リモートPHPスクリプト作成 & 実行
remote_insert_php = """<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');
require_once(ABSPATH . 'wp-admin/includes/file.php');
require_once(ABSPATH . 'wp-admin/includes/media.php');

$json = file_get_contents('new_posts_payload.json');
$posts = json_decode($json, true);

$theme_dir = get_template_directory();

foreach ($posts as $item) {
    // 既存記事の重複チェック
    $existing = get_page_by_path($item['slug'], OBJECT, 'post');
    $category = get_category_by_slug($item['category_slug']);
    $cat_ids = $category ? array($category->term_id) : array();
    
    $post_data = array(
        'post_title'    => $item['title'],
        'post_content'  => $item['content'],
        'post_status'   => 'publish',
        'post_name'     => $item['slug'],
        'post_type'     => 'post',
        'post_category' => $cat_ids,
        'post_author'   => 1,
    );
    
    if ($existing) {
        $post_data['ID'] = $existing->ID;
        $post_id = wp_update_post($post_data);
        echo "Updated existing post ID: $post_id\\n";
    } else {
        $post_id = wp_insert_post($post_data);
        echo "Created new post ID: $post_id\\n";
    }
    
    if (is_wp_error($post_id)) {
        echo "Error: " . $post_id->get_error_message() . "\\n";
        continue;
    }
    
    // アイキャッチ画像の設定
    $thumb_path = $theme_dir . '/assets/images/thumbnails/' . $item['thumb_file'];
    if (file_exists($thumb_path)) {
        $wp_upload_dir = wp_upload_dir();
        $filename = basename($thumb_path);
        $unique_filename = wp_unique_filename($wp_upload_dir['path'], $filename);
        $upload_file = $wp_upload_dir['path'] . '/' . $unique_filename;
        
        copy($thumb_path, $upload_file);
        
        $filetype = wp_check_filetype($unique_filename, null);
        $attachment = array(
            'post_mime_type' => $filetype['type'],
            'post_title'     => sanitize_file_name($unique_filename),
            'post_content'   => '',
            'post_status'    => 'inherit'
        );
        $attach_id = wp_insert_attachment($attachment, $upload_file, $post_id);
        $attach_data = wp_generate_attachment_metadata($attach_id, $upload_file);
        wp_update_attachment_metadata($attach_id, $attach_data);
        
        set_post_thumbnail($post_id, $attach_id);
        echo "Set featured image (Attachment ID: $attach_id) for Post ID: $post_id\\n";
        echo "URL: " . get_permalink($post_id) . "\\n";
    }
}

// キャッシュパージ
if (function_exists('opcache_reset')) {
    opcache_reset();
    echo "OPcache reset successfully.\\n";
}
if (defined('LSCWP_V')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed cache purged.\\n";
}
"""

with sftp.open('insert_posts_tmp.php', 'w') as f:
    f.write(remote_insert_php)

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php insert_posts_tmp.php')
out = stdout.read().decode('utf-8')
err = stderr.read().decode('utf-8')
print(out)
if err:
    print("ERR:", err)

ssh.exec_command('rm insert_posts_tmp.php new_posts_payload.json')
sftp.close()
ssh.close()
print("New posts published successfully!")
