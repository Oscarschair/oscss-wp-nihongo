import paramiko
import json
import base64
import sys

sys.stdout.reconfigure(encoding='utf-8')

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

# Gutenberg blocks for About page
content_blocks = """<!-- wp:html -->
<div class="c-about-profile-card" style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; margin-bottom: 32px; box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04); display: flex; gap: 20px; align-items: center; flex-wrap: wrap;">
  <img src="https://nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/my-icon.png" alt="オスカー" style="width: 76px; height: 76px; border-radius: 50%; object-fit: cover; border: 2px solid #3b82f6; flex-shrink: 0;" />
  <div style="flex: 1; min-width: 240px;">
    <div style="font-size: 1.2rem; font-weight: 700; color: #0f172a; margin-bottom: 6px;">サイト管理者：オスカー（Oscar）</div>
    <div style="font-size: 0.92rem; color: #475569; line-height: 1.65;">
      香港出身・日本在住。一人の外国人学習者として日本語の奥深さや難しさと向き合いながら、教科書では学べない「リアルな日本語」「文化の違い」「カルチャーショック」を独自の視点でお届けしています。
    </div>
  </div>
</div>
<!-- /wp:html -->

<!-- wp:paragraph -->
<p>「オスカーの日本語学習帳」にお越しいただき、本当にありがとうございます！</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>当サイトは、日本語を第二言語として学んできた運営者「オスカー」が、外国人学習者としての実体験や日本での生活を通じて学んだ「リアルな日本語」「ことばのあや」「文化の違い」「カルチャーショック」を独自の視点からお届けする個人学習ノートです。</p>
<!-- /wp:paragraph -->

<!-- wp:html -->
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin: 28px 0 36px;">
  <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
    <div style="font-weight: 700; color: #0f172a; margin-bottom: 8px; font-size: 1.05rem; display: flex; align-items: center; gap: 8px;">
      <span style="font-size: 1.3rem;">🚫</span> 営業・勧誘ゼロ
    </div>
    <p style="font-size: 0.88rem; color: #475569; margin: 0; line-height: 1.6;">有料教材の販売やオンラインサロン、スクール等の勧誘は一切ありません。安心して無料でご利用いただけます。</p>
  </div>
  <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
    <div style="font-weight: 700; color: #0f172a; margin-bottom: 8px; font-size: 1.05rem; display: flex; align-items: center; gap: 8px;">
      <span style="font-size: 1.3rem;">☕</span> 広告 ＆ チップ応援で運営
    </div>
    <p style="font-size: 0.88rem; color: #475569; margin: 0; line-height: 1.6;">当サイトの維持費は広告収入および <a href="https://buymeacoffee.com/oscarchair" target="_blank" rel="noopener" style="color: #d97706; font-weight: 600; text-decoration: underline;">Buy Me a Coffee</a> での温かい応援により賄われています。</p>
  </div>
  <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
    <div style="font-weight: 700; color: #0f172a; margin-bottom: 8px; font-size: 1.05rem; display: flex; align-items: center; gap: 8px;">
      <span style="font-size: 1.3rem;">📖</span> 文章の引用は自由
    </div>
    <p style="font-size: 0.88rem; color: #475569; margin: 0; line-height: 1.6;">事前許諾不要で自由に引用可能です。出典としてサイトや記事のURLを記載していただけますと幸いです。</p>
  </div>
</div>
<!-- /wp:html -->

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">1. サイト管理者（オスカー）について</h2>
<!-- /wp:heading -->

<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">日本語教師ではなく、一人の「日本語学習者」です</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>私、オスカーはプロの日本語教師や言語学者ではありません。母語ではない日本語をゼロから学び、日本での暮らしや仕事を通じて日々日本語の奥深さや難しさと向き合っている<strong>「一人の外国人学習者」</strong>です。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>教科書通りの文法解説だけでは捉えきれない、リアルな疑問や感覚を大切にしています。</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
  <li>「日常会話でよく耳にするあの言葉、本当はどういうニュアンスなんだろう？」</li>
  <li>「なぜ日本人はこの場面でこういう言い回しをするのだろう？」</li>
  <li>「似ている類語の使い分けは、実際の生活ではどう感じられているのだろう？」</li>
</ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>外国人学習者だからこそ気づく素朴な疑問や「つまずきポイント」を、分かりやすく整理・共有することを大切にしています。</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">営業・教材販売・勧誘は一切ございません</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>当サイトでは、<strong>有料教材の販売、オンラインサロンやスクールへの勧誘、情報商材の営業などは一切行っておりません。</strong></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>「日本語を楽しく、安心して学べる場にしたい」という想いから立ち上げた個人サイトですので、どなたでもすべてのコンテンツを完全無料で安心してご覧いただけます。</p>
<!-- /wp:paragraph -->

<!-- wp:separator {"className":"is-style-wide"} -->
<hr class="wp-block-separator has-alpha-channel-opacity is-style-wide"/>
<!-- /wp:separator -->

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">2. サイトの運営と広告収入について</h2>
<!-- /wp:heading -->

<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">サイト利益は「広告収入のみ」で運営しています</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>当サイトのサーバー維持費やドメイン代、コンテンツの作成にかかる運営費用は、すべてサイト内に掲載されている<strong>「広告収入（Google AdSense等）」のみ</strong>によって賄われています。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>有料会員制や課金要素は設けておらず、世界中どこからでも自由にアクセスできるオープンな学習ノートであり続けることを目指しています。</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">サイトを応援していただける読者の皆様へ</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>もし当サイトの記事が日本語学習のお役に立ったり、「面白い！」「応援したいな」と感じていただけましたら、<strong>サイト内に表示される広告をご覧いただいたり、気になった広告をクリックしていただけますと幸いです。</strong></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>皆様のささやかな応援がダイレクトにサイトの維持費となり、次なる記事の執筆やコンテンツ改善の大きな原動力になります。温かいご支援を心より感謝申し上げます。</p>
<!-- /wp:paragraph -->

<!-- wp:html -->
<div class="c-bmc-card">
  <img src="https://nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/bmc-banner.webp" alt="Buy Me a Coffee - オスカーの日本語学習帳応援バナー" class="c-bmc-card__banner" loading="eager" width="800" height="280" />
  <div class="c-bmc-card__body">
    <div class="c-bmc-card__title">
      <span class="c-bmc-card__title-main">☕ Buy Me a Coffee</span>
      <span class="c-bmc-card__title-sub">（直接応援窓口）</span>
    </div>
    <p class="c-bmc-card__desc">
      「広告だけでなく直接応援したい！」「オスカーにコーヒーを1杯奢りたい！」と思っていただける読者様のために、少額（1杯分〜）から応援いただける窓口を開設しております。温かいご支援をサイト維持や教材づくりの励みとして大切に活用させていただきます！
    </p>
    <a href="https://buymeacoffee.com/oscarchair" target="_blank" rel="noopener noreferrer" class="c-bmc-btn">
      <svg class="c-bmc-btn__icon" viewBox="0 0 24 24" fill="currentColor"><path d="M20.216 6.415l-.132-.666c-.119-.597-.384-1.144-.768-1.583-.733-.837-1.841-1.166-3.123-1.166H4.218C2.584 3 1.25 4.334 1.25 5.968v9.064c0 1.634 1.334 2.968 2.968 2.968h9.064c1.634 0 2.968-1.334 2.968-2.968v-1.077h2.842c1.282 0 2.39-.329 3.123-1.166.384-.439.649-.986.768-1.583l.132-.666c.219-1.1.219-2.025 0-3.125zm-2.109 4.887c-.198.226-.532.348-.992.348h-2.842V6.368h2.842c.46 0 .794.122.992.348.204.233.29.569.255 1.002l-.132.666c-.035.176-.07.353-.105.53-.035.177-.07.354-.105.53l.132.666c.035.433-.051.769-.255 1.002z"/></svg>
      <span class="c-bmc-btn__text">オスカーにコーヒーを奢る</span>
      <span class="c-bmc-btn__subtext">(Buy Me a Coffee)</span>
    </a>
  </div>
</div>
<!-- /wp:html -->

<!-- wp:separator {"className":"is-style-wide"} -->
<hr class="wp-block-separator has-alpha-channel-opacity is-style-wide"/>
<!-- /wp:separator -->

<!-- wp:html -->
<div class="c-no-ads-zone google-anno-skip no-ads adsbygoogle-noab adsbygoogle-noablate" data-google-anno-skip="true" data-ad-exclude="true" data-ad-status="unfilled">
<!-- /wp:html -->

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">3. 文章の引用・転載について</h2>
<!-- /wp:heading -->

<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">引用は自由にしていただいて構いません</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>当サイトに掲載している文章や解説内容は、<strong>学習、研究、個人ブログ、SNS、教育現場・プリント作成などにおいて自由に引用・ご活用いただいて構いません。</strong></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>事前のご連絡や許諾申請も不要です。日本語の理解を深めるためのお役に立てれば幸いです。</p>
<!-- /wp:paragraph -->

<!-- wp:html -->
<div class="c-no-ads-subzone google-anno-skip no-ads adsbygoogle-noab adsbygoogle-noablate" data-google-anno-skip="true" data-ad-exclude="true" data-ad-status="unfilled" style="margin: 24px 0;">
<!-- /wp:html -->

<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">引用時のお願い：URLの記載</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>文章を引用される際は、<strong>引用元の記事URL（または当サイトのURL）を明記（リンク）</strong>していただけますようお願いいたします。</p>
<!-- /wp:paragraph -->

<!-- wp:html -->
<div style="background: #f1f5f9; border-left: 4px solid #3b82f6; border-radius: 4px; padding: 14px 18px; margin: 16px 0; font-family: monospace; font-size: 0.9rem; color: #334155; line-height: 1.6;">
  <strong>【引用表記の例】</strong><br />
  出典：オスカーの日本語学習帳（<a href="https://nihongo.oscarchair.jp/" target="_blank" rel="noopener">https://nihongo.oscarchair.jp/</a>）<br />
  出典記事：[該当記事タイトル]（https://nihongo.oscarchair.jp/該当記事URL/）
</div>
<!-- /wp:html -->

<!-- wp:paragraph -->
<p>正しい情報元の共有と、他の学習者の方への認知向上のため、ご協力いただけますと幸いです。</p>
<!-- /wp:paragraph -->

<!-- wp:html -->
</div>
</div>
<!-- /wp:html -->

<!-- wp:separator {"className":"is-style-wide"} -->
<hr class="wp-block-separator has-alpha-channel-opacity is-style-wide"/>
<!-- /wp:separator -->

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">4. 日本語を学ぶすべての人と、日本語教師の皆様へ</h2>
<!-- /wp:heading -->

<!-- wp:html -->
<div style="background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%); border-left: 5px solid #0284c7; border-radius: 10px; padding: 22px; margin: 24px 0; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
  <div style="font-weight: 700; color: #0369a1; font-size: 1.1rem; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
    <span>🌏</span> 日本語を学ぶ仲間の皆さんへ
  </div>
  <p style="color: #334155; margin: 0; line-height: 1.7; font-size: 0.95rem;">
    日本語は、ひらがな・カタカナ・漢字の3種類の文字体系に加え、繊細な敬語表現や終助詞（「ね」「よ」など）、文脈によって意味が変わるニュアンスなど、非常に奥が深く、時には学習に挫折しそうになることもあると思います。<br /><br />
    私自身も同じように悩み、試行錯誤を繰り返してきました。一歩ずつの積み重ねが必ず力になります。当サイトが皆さんの日本語学習の小さなヒントや息抜きになればとても嬉しいです。一緒に楽しく学んでいきましょう！
  </p>
</div>

<div style="background: linear-gradient(135deg, #fefce8 0%, #fff7ed 100%); border-left: 5px solid #ea580c; border-radius: 10px; padding: 22px; margin: 24px 0; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
  <div style="font-weight: 700; color: #c2410c; font-size: 1.1rem; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
    <span>🎓</span> 日本語教育に携わる教師・講師の皆様へ
  </div>
  <p style="color: #334155; margin: 0; line-height: 1.7; font-size: 0.95rem;">
    日々、熱心に日本語教育に携わり、多くの外国人学習者を温かく導いてくださっている日本語教師の皆様に心より深く敬意を表します。<br /><br />
    外国人学習者ならではの「つまずきポイント」や「文化的な違和感・カルチャーショック」の記録が、実際の授業の導入や雑談のネタ、教材づくりのヒントとして少しでもお役に立てば幸いです。<br /><br />
    学習者の未来を拓く先生方の素晴らしい活動を、心より応援しております。どうぞ頑張ってください！
  </p>
</div>
<!-- /wp:html -->

<!-- wp:separator {"className":"is-style-wide"} -->
<hr class="wp-block-separator has-alpha-channel-opacity is-style-wide"/>
<!-- /wp:separator -->

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">運営者情報まとめ</h2>
<!-- /wp:heading -->

<!-- wp:table {"className":"is-style-stripes"} -->
<figure class="wp-block-table is-style-stripes"><table><tbody>
<tr><td style="font-weight: 600; width: 30%;">サイト名</td><td>オスカーの日本語学習帳（Oscar's Japanese Notebook）</td></tr>
<tr><td style="font-weight: 600;">サイトURL</td><td><a href="https://nihongo.oscarchair.jp/">https://nihongo.oscarchair.jp/</a></td></tr>
<tr><td style="font-weight: 600;">運営者</td><td>オスカー（Oscar）</td></tr>
<tr><td style="font-weight: 600;">運営方針</td><td>完全無料・広告収入による独立運営（営業・教材販売・勧誘なし）</td></tr>
<tr><td style="font-weight: 600;">引用方針</td><td>URL明記の上で引用自由（事前申請不要）</td></tr>
<tr><td style="font-weight: 600;">応援窓口</td><td><a href="https://buymeacoffee.com/oscarchair" target="_blank" rel="noopener">Buy Me a Coffee（buymeacoffee.com/oscarchair）</a></td></tr>
<tr><td style="font-weight: 600;">関連サイト</td><td><a href="https://oscarchair.jp/" target="_blank" rel="noopener">オスカーのAIノート（oscarchair.jp）</a></td></tr>
</tbody></table></figure>
<!-- /wp:table -->
"""

payload = [
    {
        "title": "日本語学習帳について",
        "slug": "about",
        "content": content_blocks
    }
]

payload_b64 = base64.b64encode(json.dumps(payload, ensure_ascii=False).encode('utf-8')).decode('utf-8')

php_script = f"""<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$b64 = '{payload_b64}';
$pages = json_decode(base64_decode($b64), true);

foreach ($pages as $p) {{
    $title = $p['title'];
    $slug = $p['slug'];
    $content = $p['content'];
    
    $existing = get_posts(array(
        'name' => $slug,
        'post_type' => 'page',
        'post_status' => 'any',
        'numberposts' => 1
    ));
    
    if (!empty($existing)) {{
        $page_id = $existing[0]->ID;
        wp_update_post(array(
            'ID' => $page_id,
            'post_title' => $title,
            'post_content' => $content,
            'post_status' => 'publish'
        ));
        echo "Updated page $slug (ID: $page_id)\\n";
    }} else {{
        $page_id = wp_insert_post(array(
            'post_title' => $title,
            'post_content' => $content,
            'post_name' => $slug,
            'post_type' => 'page',
            'post_status' => 'publish',
            'post_author' => 1
        ));
        echo "Created page $slug (ID: $page_id)\\n";
    }}
}}

if (defined('LSCWP_V')) {{
    do_action('litespeed_purge_all');
}}
if (function_exists('opcache_reset')) {{
    @opcache_reset();
}}
echo "SUCCESS\\n";
"""

sftp = ssh.open_sftp()
remote_script = 'web/nihongo.oscarchair.jp/deploy_about_temp.php'
with sftp.open(remote_script, 'w') as f:
    f.write(php_script)

stdin, stdout, stderr = ssh.exec_command(f"/usr/local/php/8.2/bin/php {remote_script}")
print(stdout.read().decode('utf-8'))
sftp.remove(remote_script)
sftp.close()
ssh.close()
