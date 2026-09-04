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

posts_content = {}

# ==========================================
# POST 1: 「ごめんなさい」VS「すみません」
# ==========================================
posts_content[1] = f"""{make_balloon('オスカー', oscar_avatar, 'l', [
    'こんにちは、オスカーです。',
    '「ごめんなさい」と「すみません」は、どちらも日常的によく使う謝罪の言葉ですが、そのニュアンスや使われる場面には明確な違いがあります。',
    'さて、「『ごめんなさい』と『すみません』はどう違うの？」と聞かれたとき、すぐに答えられますか？',
    '私は以前、職場の同僚5〜6人に聞いてみたことがあるのですが、即答できた人はゼロ（私のクイズ勝率100%！）でした。',
    'ぜひ最後までお読みいただけますと幸いです。'
])}

<!-- wp:heading -->
<h2>答え：「自分に非があると思っているか」の違い</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>結論から言うと、この2つは「自分に非（悪かったこと・過失）があると思っているかどうか」で使い分けられています。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>具体的な使い分けの例</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>身近な例で考えてみましょう。<br>例えば、満員電車に乗っていて駅に到着したとき、ドアから離れた奥の位置にいたら何と声をかけて前へ進むでしょうか？</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>多くの方は、「すみません！降ります！」と声をかけながら進むと思います。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>これは、「私が悪いわけではありませんが、降りたいので前を開けていただけますか（恐縮です・失礼します）」というニュアンスで「すみません」を使っています。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>では、電車を降りる途中で、うっかり誰かの足を踏んでしまったときはどうでしょうか？</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>その場合は、「ごめんなさい！」（あるいは「大変失礼いたしました！」）と謝るのが自然で適切です。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>これは、「足を踏んでしまったのは完全に自分の不注意であり、自分が悪い」という自覚と反省があるためです。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>「罪の意識（責任）」の有無</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>もう少し詳しく掘り下げてみましょう。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>まず、「ごめんなさい」は、明確な誤りや失敗・過失をしてしまったときに使われます。<br>直接的な謝罪の表現であり、自分の行動に対して相手に深くお詫びするときに用います。例えば、友達との約束を破ってしまったときや、大事な物を壊してしまったときに使います。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>一方、「すみません」は、相手にちょっとした手間や迷惑をかけたり、呼びかけたりするときに使われます。<br>深い謝罪というよりは、「恐縮ですが」「失礼します」と軽く相手の配慮を求めたり感謝を込めたりする印象を与えます。例えば、電車で人と軽く肩が触れたときや、店員さんを呼ぶとき、誰かに手伝ってもらうときに使います。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>つまり、「ごめんなさい」は「自分に非がある」という責任感・反省があるときに使います。大げさに言えば、「罪の意識」の有無で使い分けていると言えます。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>そのため、自分の明らかな過失で相手に大きな迷惑をかけたにもかかわらず、「すみません」とだけ軽く流してしまうと、「反省していない」「適当に謝られた」と相手を怒らせてしまう原因にもなるので注意が必要です。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>おわりに</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>同じお詫びの言葉であっても、状況に応じた使い分けを誤ると大変失礼になってしまうことがあります。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>言葉の背景にあるニュアンスを理解して、気持ちの良いコミュニケーションを心がけたいですね。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>今日も最後まで読んでいただき、ありがとうございました。<br>お役に立てれば幸いです。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>それでは！</p>
<!-- /wp:paragraph -->"""

# ==========================================
# POST 30: 日本の奨学金 VS 海外漢字圏の奨学金
# ==========================================
posts_content[30] = f"""{make_balloon('オスカー', oscar_avatar, 'l', [
    'こんにちは、オスカーです。',
    '以前、職場の新入社員と雑談していたときに、「毎月、奨学金の返済が大変で…」という話題が出ました。',
    '「えっ、『奨学金』なのに返済が必要ってどういうこと！？」と、私の頭の中は一瞬で大混乱（カオス）になりました。',
    '今回は、日本と海外漢字圏における「奨学金」という言葉の大きな違いについてお話しします。'
])}

<!-- wp:heading -->
<h2>日本の奨学金制度</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>気になって日本の奨学金制度について調べてみたところ、以下のような仕組みになっていることが分かりました。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>日本の奨学金には大きく分けて「給付型奨学金」と「貸与型奨学金」があります。<br>・<strong>給付型奨学金</strong>：返済が不要なもの<br>・<strong>貸与型奨学金</strong>：卒業後に返済が必要なもの（無利子・有利子あり）</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>日本で単に「奨学金」と呼ぶ場合、一般的にはこの<strong>貸与型（＝学生向けローン）</strong>を指すケースが非常に多いようです。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>海外（漢字圏）の奨学金</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>もちろん海外にも「奨学金」という概念は存在します。<br>ここでは特に、同じ漢字文化を持つ中華圏（中国・台湾・香港など）を例にお話しします。中華圏でも「奨学金（奖学金 / 獎學金）」という制度は一般的です。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>しかし海外漢字圏では、<strong>原則として返済が不要なものだけを「奨学金」と呼びます</strong>。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>海外での「奨学金」は、学業成績が極めて優秀な学生や、優れた研究成果を上げた人に対して、「よく頑張ったね」「これからも励んでほしい」と学校や財団から贈られる<strong>褒賞（アワード・賞金）</strong>だからです。そのため、返済の義務は一切ありません。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>「奨」という漢字の意味の違い</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>なぜこのような違いが生まれるのでしょうか？<br>それは「奨」という漢字の捉え方にあります。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>日本の奨学金における「奨」は、主に学業を<strong>「奨励（応援・後押し）」</strong>するという意味合いで使われており、経済的な就学支援（ファイナンスサポート）全般を指しています。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>一方、海外漢字圏の「奨（獎）」は<strong>「賞（褒美・表彰）」</strong>の意味が非常に強く、優秀な実績に対する「アワード」を意味します。例えば「学年1位の成績を取った学生には全学費免除＋賞金支給」といった給付金が「奨学金」に当たります。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>海外には「貸与型」の制度はないの？</h2>
<!-- /wp:heading -->

{make_balloon('オスカー', oscar_avatar, 'l', [
    'ここまで聞くと、「じゃあ海外には日本のような学費の貸与・融資制度はないの？」と思われるかもしれません。'
])}

<!-- wp:paragraph -->
<p>もちろんあります。ただし海外漢字圏では、それを「奨学金」とは呼ばず、<strong>「助学金（助學金）」</strong>と明確に呼び分けています。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>「助学金」は、文字通り「就学・学びを助ける（経済的困難を支援する）」という意味の資金です。経済状況に応じて全額または一部が支援され、返済が必要な貸与型の制度もここに含まれます。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>おわりに</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>同じ「奨学金」という漢字表記であっても、文化や国が違えば意味や実態がまったく異なります。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>特に教育資金やおカネに関わる言葉だからこそ、海外出身者からすると最初のカルチャーショックになりやすいポイントの一つです。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>今日も最後まで読んでいただき、ありがとうございました。<br>お役に立てれば幸いです。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>それでは！</p>
<!-- /wp:paragraph -->"""

# ==========================================
# POST 36: 「おもしろい」VS「おかしい」
# ==========================================
posts_content[36] = f"""{make_balloon('オスカー', oscar_avatar, 'l', [
    'こんにちは、オスカーです。',
    '「おもしろい」と「おかしい」は、両方とも楽しさや喜びの感情を表す言葉ですが、微妙に意味や使う場面が異なります。その違いは何でしょうか？',
    'なんとなく感覚では分かるけれど、いざ説明しようとすると難しいと感じる方が多いのではないでしょうか？',
    '今回はその違いについて、分かりやすく解説します。',
    'ぜひ最後までお読みいただけますと幸いです。'
])}

<!-- wp:heading -->
<h2>一般的な解釈</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>「おもしろい」と「おかしい」の違いについて、「そんなに難しくないのでは？」と思われるかもしれません。まずは以下の会話を見てみましょう。</p>
<!-- /wp:paragraph -->

{make_balloon('外国の人', man_avatar, 'l', [
    '「おもしろい」と「おかしい」はどう違いますか？'
])}

{make_balloon('日本の友人', woman_avatar, 'r', [
    '「おもしろい」はあることに対して「楽しいな」と感じて、肯定的な気持ちを表す言葉です。「おかしい」は逆で、普通と違って「よくないな、変だな」と思ったときの感情表現ですよ。'
])}

{make_balloon('外国の人', man_avatar, 'l', [
    'でも、先生から「おかしい」も肯定的に笑うときに使うと聞きました。「おもしろい」とはどう違うんですか？'
])}

{make_balloon('日本の友人', woman_avatar, 'r', [
    'ああ…それは先生に詳しく聞いたほうがいいかもしれません…。'
])}

<!-- wp:paragraph -->
<p>「おかしい」が否定的な場面（Strange / Wrong）で使われることは、みなさんもよくご存じだと思います。難しいのは、<strong>肯定的な意味で使う「おかしい（Funny / Hilarious）」と「おもしろい（Interesting / Fun）」の区別</strong>ですね。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>オスカーの答え：感情の度合い（スケール）で使い分け</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p><strong>※以下の解釈はオスカー独自の視点によるものですが、共感していただけますと幸いです。</strong></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>喜びや笑いの感情レベルを「0から10」のスケールで表すと、以下のように整理できます。</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li><strong>0以下</strong>：否定的な「おかしい」（違和感・不審・変だ）</li>
<li><strong>0〜10</strong>：「おもしろい」（興味深い・楽しい・知的好奇心）</li>
<li><strong>10以上</strong>：肯定的な「おかしい」（爆笑・腹筋崩壊・ツボにはまった）</li>
</ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>肯定的な「おかしい」を使うときは、まさに<strong>腹筋崩壊レベルで大笑いしているとき</strong>が多く、逆に冷静なトーンで「それ、おかしいよね」と言うときは大体否定的な意味になります。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>その中間にある、適度で心地よい楽しさや知的な興味を表すのが「おもしろい」です。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>それぞれの例文とニュアンス</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>改めてそれぞれの意味と使い分けを見てみましょう。</p>
<!-- /wp:paragraph -->

<!-- wp:heading {{"level":3}} -->
<h3>1. 「おもしろい」</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>興味深く楽しめる、感心するような内容や状況を表現するときに使います。<br>英語で言うと <strong>Interesting</strong> や <strong>Fun</strong> のニュアンスです。</p>
<!-- /wp:paragraph -->

<!-- wp:quote -->
<blockquote class="wp-block-quote"><p><strong>例文</strong>：「あの小説、超おもしろいから絶対に読んだほうがいいよ！」</p></blockquote>
<!-- /wp:quote -->

<!-- wp:paragraph -->
<p>小説や映画、スポーツ観戦などで内容やストーリーに対して肯定的な印象を与えるときによく使われます。また、人や物の個性・性格について「魅力的だ」と感じたときにも用いられます。</p>
<!-- /wp:paragraph -->

<!-- wp:heading {{"level":3}} -->
<h3>2. 「おかしい」</h3>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>予想外の出来事や奇妙な状況、滑稽な出来事を表現するときに使います。<br>基本的には「普通の状態からズレている（違和感）」を表す言葉です。</p>
<!-- /wp:paragraph -->

<!-- wp:quote -->
<blockquote class="wp-block-quote"><p><strong>否定の例文</strong>：「その計算はおかしいよ、もう一回確認してみて」（Wrong / Strange）<br><strong>肯定の例文</strong>：「今の漫才はおかしいｗｗ 腹筋が痛い！」（Hilarious / Funny）</p></blockquote>
<!-- /wp:quote -->

<!-- wp:paragraph -->
<p>漫才やコントなど、想像をはるかに超えるボケやハプニングを見て笑いがこみ上げてくるとき、私たちは「おかしい」という言葉を使います。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>おわりに</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>ひとつの「笑い」や「楽しさ」という感情でも、使う言葉によって当時の感情の度合いや伝わり方が変わってきます。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>日常生活で神経質に使い分ける必要はありませんが、この違いを知っておくと、日本語の奥深さがさらに実感できて面白いと思います。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>今日も最後まで読んでいただき、ありがとうございました。<br>お役に立てれば幸いです。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>それでは！</p>
<!-- /wp:paragraph -->"""

# ==========================================
# POST 44: ご飯の形を整える日本食
# ==========================================
posts_content[44] = f"""{make_balloon('オスカー', oscar_avatar, 'l', [
    'こんにちは、オスカーです。',
    '今回は、食文化にまつわるカルチャーショックをご紹介します。',
    'テーマは「ご飯（白米・チャーハン）の盛り付け方」について。人によっては「えっ、そんな細かいところに？」と思われるかもしれません。',
    '記事の後半では、この盛り付け方から見分ける「本当に本場の中華・中国料理店の見つけ方」についてもご紹介します。',
    'ぜひ最後までお読みいただければ幸いです。',
    '※オスカーは香港出身で、ここでのお話は私個人の実体験や文化背景に基づいています。'
])}

<!-- wp:heading -->
<h2>ご飯の盛り付け方ショック</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>日本の飲食店やご家庭でご飯をよそうとき、お茶碗にご飯を盛って、しゃもじで表面をトントンと丸く整えたり、ドーム状にきれいに成形したりすることはよくありますよね。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>さらにカレーライスやオムライスのとき、一度お茶碗にご飯をぎゅっと押し込んでから、お皿の上にパカッとひっくり返して盛り付ける場面もよく見かけます。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>実はこれこそが、今回お話ししたいカルチャーショックなのです。</p>
<!-- /wp:paragraph -->

{make_balloon('日本の方', man_avatar, 'r', [
    'え？ ご飯の形を整えるのって綺麗に見せるためだし普通じゃない？ どこにショックポイントがあるの？'
])}

<!-- wp:paragraph -->
<p>私たちが気になるのは、しゃもじで<strong>「ご飯の形を押し固めて整える」</strong>という点です。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>実は私の育った環境では、ご飯を押し固める行為は「やってはいけないお作法」として教えられてきました。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>ご先祖様と生きている人間の境界線</h2>
<!-- /wp:heading -->

{make_balloon('日本の方', man_avatar, 'r', [
    'なるほど、ご飯をしゃもじで押し潰すと、ふんわりしたお米の食感が損なわれてしまうからかな？'
])}

<!-- wp:paragraph -->
<p>もちろん食感の理由もありますが、もっと深い文化的な理由があります。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>家庭によって異なる部分もありますが、私の家では昔からこう教えられていました。<br><strong>「しゃもじでご飯をぎゅっと押し固めるのは、ご先祖様へのお供えご飯だけ。生きている人間が食べるご飯を押して固めてはいけない」</strong></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>我が家にはご先祖様の位牌（仏壇）があり、夕食の際には、炊きたての一番最初のご飯を少しだけご先祖様にお供えしていました。<br>その際、神仏やご先祖様にお供えするご飯は、綺麗に形を整えて押し固めるのが作法でした。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>つまり、「ご飯を押し固めるかどうか」が、<strong>ご先祖様へのお供えと、人間が日常でいただく食事との境界線（けじめ）</strong>を分ける大切な意味を持っていたのです。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>そのため、日本に来た当初、定食屋さんのご飯まで綺麗なドーム型に整えられているのを見て、思わず「ドキッ」としてしまった記憶があります。</p>
<!-- /wp:paragraph -->

{make_balloon('オスカー', oscar_avatar, 'l', [
    '（※もちろん現在は、日本の美しい盛り付け文化として美味しくいただいています！）'
])}

<!-- wp:heading -->
<h2>盛り付けでわかる「本場中国料理店」の見つけ方</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>さて、ここからは「本場中国料理店の見つけ方」についてお話しします。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>実はそれも、<strong>「チャーハンの盛り付け方」</strong>を見れば一目で分かります。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>日本のみなさんが思い浮かべるチャーハンは、お玉を使ってドーム状に丸く整えられたこんな形ではないでしょうか？</p>
<!-- /wp:paragraph -->

<!-- wp:image {{"id":46,"sizeSlug":"large","linkDestination":"none"}} -->
<figure class="wp-block-image size-large"><img src="https://nihongo.oscarchair.jp/wp-content/uploads/2023/03/image-1024x456.png" alt="日本の一般的なチャーハンのイメージ" class="wp-image-46"/><figcaption class="wp-element-caption">日本の一般的なチャーハンのイメージ</figcaption></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>オスカーの個人的なこだわりかもしれませんが、綺麗に半球状に押し固められたチャーハンは、香港や中国の感覚からすると「日本向けにアレンジされたスタイル（町中華）」と言えます。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>本場の中国料理店では、中華鍋からそのままフワッとお皿に移され、パラパラとしたお米の質感がそのまま残るように無造作に盛られます。</p>
<!-- /wp:paragraph -->

<!-- wp:image {{"sizeSlug":"large","linkDestination":"none"}} -->
<figure class="wp-block-image size-large"><img src="https://tblg.k-img.com/restaurant/images/Rvw/89988/640x640_rect_89988214.jpg" alt="満州王さんの卵チャーハン" class="wp-image-89988214"/><figcaption class="wp-element-caption">満州王さんの卵チャーハン（本場スタイルの盛り付け）</figcaption></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>もし街で中華料理店に入った際、チャーハンがドーム型ではなく、お皿の上にふわっとパラパラに盛られて出てきたら、そのお店は「本場の味付け・調理法」に強いこだわりを持っている可能性が高いです！</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>おわりに</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>今回は、ご飯の盛り付け方にまつわる食文化のカルチャーショックについてお話ししました。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>「え、そんなところにも違いがあるの？」という日常のちょっとした発見は、異文化のとても面白い魅力です。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>今後もこうした体験談や文化の違いを発信していきますので、ぜひお楽しみに！</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>今日も最後まで読んでいただき、ありがとうございました。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>それでは！</p>
<!-- /wp:paragraph -->"""

# ==========================================
# POST 19: 終助詞「ね」の使い方について
# ==========================================
posts_content[19] = f"""{make_balloon('オスカー', oscar_avatar, 'l', [
    'こんにちは、オスカーです。',
    'みなさんは普段、語尾の「ね」の使い方を意識したことはありますでしょうか？',
    'これは日本語学習者（外国人）に限った話ではなく、実はネイティブの日本人同士でもよく起こるすれ違いのポイントです。',
    '私は以前、仕事のプロジェクト管理をしている際、社外の日本人担当者とのやり取りで「この場面での『ね』の使い方は少しおかしいかも？」と強い違和感を覚えた経験があります。',
    '今回はこの終助詞「ね」の正しい役割と使い分けについて考えてみましょう。'
])}

<!-- wp:heading -->
<h2>違和感のあるビジネス事例</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>まずは実際のやり取りの例を見てみましょう。</p>
<!-- /wp:paragraph -->

{make_balloon('プロジェクト責任者', woman_avatar, 'l', [
    'この画面、本来は企業ロゴが表示されるべき仕様ですが、現在消えてしまっています。何か原因は分かりますでしょうか？'
])}

{make_balloon('担当者', man_avatar, 'r', [
    'なるほどですね。。わからないですね。。'
])}

<!-- wp:paragraph -->
<p>いかがでしょうか？<br>この会話を見て、何かモヤモヤした違和感を感じませんでしたか？</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>実は、ここの「わからないですね」という「ね」の使い方は、ビジネスにおいて非常に危険な使われ方です。<br>なぜ違和感があるのか、論理的に説明できますでしょうか？</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>なぜ「ね」を使ってしまうのか？</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>解説の前に、まず話し手（担当者）の心理を考えてみましょう。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>「今日はいい天気ですね」という表現は日常でよく使われますよね。<br>もし「今日はいい天気です。」と言い切られると少し冷たく感じたり、「何か機嫌が悪いのかな？」と思ったりするかもしれません。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>上記の担当者も、「わかりません」と言い切るのが怖くて、<strong>「表現を柔らかくしようとして、無意識に『ね』を付けた」</strong>のだと考えられます。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>「言葉のニュアンス」で片付けてはいけない</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>この事例について日本の知人に相談したところ、こんな答えが返ってくることがありました。</p>
<!-- /wp:paragraph>

{make_balloon('日本の知人', man_avatar, 'r', [
    'この微妙なニュアンスは日本人なら感覚で分かるんだけど、言葉で説明するのは難しいですね…'
])}

<!-- wp:paragraph -->
<p>しかし、このように「言葉のニュアンス（感覚）」に逃げてしまうと、本質的な改善につながりません。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>「なんとなく」ではなく、終助詞「ね」には明確な文法・機能上のルールが存在し、先ほどのやり取りが不適切だった理由も論理的に説明できるのです。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>終助詞「ね」が持つ4つの基本機能</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>日本語の終助詞「ね」には、主に以下の4つの機能があります。</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li><strong>1. 共感を求める</strong><br>例：「車酔いや船酔いする人は多いけど、飛行機に酔う人ってあんまりいないよね。」</li>
<li><strong>2. 共感を表す</strong><br>例：「私もそう思いますね。」</li>
<li><strong>3. 内容を確認する</strong><br>例：「オンラインでは何度もお話ししていますが、実際に対面でお会いするのは初めてですよね？」</li>
<li><strong>4. 注意喚起・話の引き止め</strong><br>例：「あれはね、今から50年前のことですけれどね…」</li>
</ul>
<!-- /wp:list -->

<!-- wp:paragraph -->
<p>これらをよく見ると、4の注意喚起を除き、<strong>「相手も同じ情報や状況を共有・理解している前提」</strong>で使われていることが分かります。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>「ね」は単に言葉を柔らかくする魔法の言葉ではない！</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>「いい天気ですね」の「ね」は、「いい天気です」を柔らかくするために付けられたのではありません。「お互いに良い天気だと分かっている」という<strong>共感を求める行為</strong>によって、結果として柔らかく聞こえているだけです。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>そのため、相手と情報や状況が共有されていない場面で「ね」を使ってしまうと、重大なコミュニケーションの齟齬が生じます。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>改めて先ほどの事例を振り返ってみましょう。</p>
<!-- /wp:paragraph -->

{make_balloon('プロジェクト責任者', woman_avatar, 'l', [
    'この画面、本来は企業ロゴが表示されるべき仕様ですが、現在消えてしまっています。何か原因は分かりますでしょうか？'
])}

{make_balloon('担当者', man_avatar, 'r', [
    'なるほどですね。。わからないですね。。'
])}

<!-- wp:paragraph -->
<p>責任者は「原因が分からないから、調べて報告してほしい」と求めているのに、担当者が「わからないですね（＝分からないですよね〜）」と同調・共感を求めてしまうと、<strong>「原因が分からないことについて私に同意を求めてどうするの？ 人ごと・無責任ではないか？」</strong>と相手の怒りを買ってしまうのです。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>この場合、以下のように返答するのがビジネスとして適切です。</p>
<!-- /wp:paragraph -->

{make_balloon('担当者', man_avatar, 'r', [
    'なるほど、承知いたしました。現時点では原因が分かりかねますので、至急調査してご報告いたします。'
])}

<!-- wp:heading -->
<h2>おわりに</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>この「ね」の使い分けミスは、日本語が流暢な外国人だけでなく、日本のビジネスパーソンの間でも無意識に多発しています。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>語尾の「ね」ひとつで、相手に「無責任」「他人事」という印象を与えてしまうことがありますので、特にビジネスの場面では状況に応じた使い分けを意識したいですね。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>今日も最後まで読んでいただき、ありがとうございました。<br>お役に立てれば幸いです。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>それでは！</p>
<!-- /wp:paragraph -->"""

# ==========================================
# POST 85: 終助詞「よ」の使い方について
# ==========================================
posts_content[85] = f"""{make_balloon('オスカー', oscar_avatar, 'l', [
    'こんにちは、オスカーです。',
    'みなさんは普段の会話で、語尾に付ける終助詞「よ」の使い方を意識したことはありますでしょうか？',
    '前回の記事では「ね」の使い方について解説しましたが、今回の主役は「よ」です。',
    '「よ」は自分の知識や感情を相手に伝えたり、注意を促したりする際に欠かせない言葉ですが、使い方次第では「上から目線」や「押し付けがましい印象」を与えてしまうこともあります。',
    '今回は終助詞「よ」の機能と、気持ちの良いコミュニケーションのためのポイントを解説します。'
])}

<!-- wp:heading -->
<h2>日常会話での事例</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>まずは簡単な日常会話の例を見てみましょう。</p>
<!-- /wp:paragraph -->

{make_balloon('友人A', man_avatar, 'l', [
    '駅前に新しくできたラーメン屋さん、本当に美味しいよ！'
])}

{make_balloon('友人B', woman_avatar, 'r', [
    'そうなんだ！ 気になってたんだよね、今度行ってみる！'
])}

<!-- wp:paragraph -->
<p>このやり取りにおける「よ」は、<strong>「相手がまだ知らない情報・自分の個人的な発見を教えてあげる」</strong>という目的で使われています。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>終助詞「よ」の主な3つの機能</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>終助詞「よ」には、主に以下の3つの役割があります。</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul>
<li><strong>1. 新情報の提供（教えてあげる）</strong><br>例：「この道をまっすぐ行くと、右手に駅が見えてくるよ。」<br>相手が知らないと思われる知識や道順を教えるときに使います。</li>
<li><strong>2. 意見や気持ちの強調（アピール）</strong><br>例：「あの映画は本当に感動したから、絶対に見るべきだよ！」<br>自分の感情やおすすめしたい度合いを強く相手に伝えるときに使います。</li>
<li><strong>3. 注意喚起・促し（警告・アドバイス）</strong><br>例：「もうすぐ電車が出発するから、急いだほうがいいよ。」<br>相手に危険や時間制限などを気づかせ、行動を促すときに使います。</li>
</ul>
<!-- /wp:list -->

<!-- wp:heading -->
<h2>ビジネスシーンや目上の人への注意点</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>「よ」の根底には「自分が知っていて、相手が知らないことを教えてあげる（伝達する）」という力関係のニュアンスが含まれています。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>そのため、目上の人や取引先に対して「〜ですよ」「〜したほうがいいですよ」を多用してしまうと、場合によっては<strong>「偉そう」「指示されている」</strong>と受け取られてしまうことがあります。</p>
<!-- /wp:paragraph -->

<!-- wp:quote -->
<blockquote class="wp-block-quote"><p><strong>ビジネスでの丁寧な言い換え例</strong>：<br>✕「その資料はもう送りましたよ。」<br>◯「その資料につきましては、先ほどメールにてお送りいたしましたのでご確認いただけますと幸いです。」</p></blockquote>
<!-- /wp:quote -->

<!-- wp:paragraph -->
<p>親しい間柄では親切心や情熱を伝える素晴らしい言葉ですが、公の場や上下関係のある場面では少し表現を工夫するのがスマートです。</p>
<!-- /wp:paragraph -->

<!-- wp:heading -->
<h2>おわりに</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>終助詞「よ」は、自分の思いや新しい情報を相手にストレートに届けるパワフルな言葉です。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>場面や相手との関係性に合わせて上手に使い分けることで、よりスムーズで心地よいコミュニケーションが生まれます。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>今日も最後まで読んでいただき、ありがとうございました。<br>お役に立てれば幸いです。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>それでは！</p>
<!-- /wp:paragraph -->"""

# SSH接続
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=host, port=port, username=user, password=password, look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

# JSONで一時保存
with sftp.open('posts_payload.json', 'w') as f:
    f.write(json.dumps(posts_content, ensure_ascii=False))

remote_update_php = """<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$json = file_get_contents('posts_payload.json');
$data = json_decode($json, true);

foreach ($data as $post_id => $content) {
    $post_id = intval($post_id);
    $res = wp_update_post(array(
        'ID'           => $post_id,
        'post_content' => $content,
    ), true);
    
    if (is_wp_error($res)) {
        echo "Error updating post $post_id: " . $res->get_error_message() . "\\n";
    } else {
        echo "Successfully updated post $post_id!\\n";
    }
}

// OPcache パージ
if (function_exists('opcache_reset')) {
    opcache_reset();
    echo "OPcache reset successfully.\\n";
}
// LiteSpeed Cache パージ
if (defined('LSCWP_V')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed cache purged.\\n";
}
"""

with sftp.open('update_posts_tmp.php', 'w') as f:
    f.write(remote_update_php)

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php update_posts_tmp.php')
out = stdout.read().decode('utf-8')
err = stderr.read().decode('utf-8')
print(out)
if err:
    print("ERR:", err)

ssh.exec_command('rm update_posts_tmp.php posts_payload.json inspect_tmp.php')
sftp.close()
ssh.close()
print("All posts updated and synchronized!")
