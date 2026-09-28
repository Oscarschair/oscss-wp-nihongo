# -*- coding: utf-8 -*-
import os
import sys
import glob

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

extra_boost_7 = {
    "2026-09-09-culture-shock-carb-on-carb-combos-in-japan-ramen-fried-rice-gyoza-rice-vermicelli.md": """
#### 炭水化物コンボをさらに楽しむための調味料マジック
定食屋の卓上には、コショウ、ラー油、お酢、醤油、七味唐辛子など多彩な調味料が並んでいます。途中でラーメンにお酢をひと回し入れたり、チャーハンに紅生姜をたっぷりのせて味を変える「味変（あじへん）」を駆使することで、最後まで飽きることなく美味しく完食することができますよ！
""",

    "2026-09-10-culture-shock-haircut-price-5000-yen-vs-1000-yen-cut-hong-kong-comparison.md": """
#### 美容室での「マッサージサービス」という至福の時間
日本の一般的な美容室では、シャンプー後やブローの前に、美容師さんが首・肩・背中を丁寧に指圧してくれるミニマッサージが標準サービスとして含まれていることがほとんどです。パソコン仕事で凝り固まった肩がほぐれるこの時間は、日本のサロンならではの温かいおもてなしの結晶です。
""",

    "2026-09-10-japanese-comparing-sayonara-and-matane-differences-in-goodbye-expressions.md": """
#### 敬語での別れ際を彩る「お気をつけて」の心遣い
夕暮れ時や雨の日の別れ際、目上の人や同僚に対して「どうぞお足元にお気をつけてお帰りください」「夜分ですので、お気をつけて」と一言添えるだけで、形式的な挨拶が相手の安全を願う温かいメッセージに昇華します。こうした小さな気配りの積み重ねが、強固な信頼関係を築く土台となります。
""",

    "2026-09-11-kotoba-no-aya-the-trap-of-daijoubu-yes-or-no-japanese-magic-phrase.md": """
#### 相手の「大丈夫」の裏にある本音を察する「共感力」
日本人は他人に迷惑をかけたくないという心理から、限界まで我慢して「大丈夫です」と微笑んでしまう傾向があります。相手が疲れた顔をしている時は、「本当に？ 無理しないでね、いつでも手伝えるからね」と一言声をかけてあげるだけで、相手の張り詰めた心がすっと軽くなります。
""",

    "2026-09-12-culture-shock-cars-stop-when-you-raise-your-hand-pedestrian-crosswalk-in-japan.md": """
#### 夜間の横断で命を守る反射材とライトの活用
夜間の日本の住宅街は街灯が控えめな場所も多く、ドライバーから黒い服を着た歩行者は非常に見えづらくなります。夜間に外出する際は、白や明るい色の服を選んだり、バッグに小さな反射キーホルダーをつけたり、スマートフォンの画面を軽く地面に向けて歩くなどの自衛意識を持つと一層安心です。
""",

    "2026-09-13-culture-shock-japanese-first-graders-walk-to-school-alone-safety-and-independence.md": """
#### 通学路に響く子供たちの元気な挨拶と地域の絆
朝の登校時間帯、小学生たちが近所の人やすれ違う大人に「おはようございます！」と元気いっぱいに挨拶する姿は、日本の住宅街の日常の風物詩です。挨拶を交わし合う関係性が街中に張り巡らされていること自体が、不審者を寄せ付けない世界最強の防犯バリアになっています。
""",

    "2026-09-15-japanese-comparing-ageru-kureru-morau-differences-in-giving-and-receiving.md": """
#### 「〜ていただく」を使いこなしてビジネス敬語を極める
「もらう」の謙譲語である「いただく」にテ形をつけた「〜ていただく」（ご案内していただく、ご確認いただく）は、ビジネスメールの最重要表現です。「ご確認してください」ではなく「ご確認いただけますと幸いです」と表現することで、相手への最高級の敬意と丁寧さが自然と伝わります。
"""
}

files = glob.glob('content/posts/*.md')
for f in files:
    base = os.path.basename(f)
    if base in extra_boost_7:
        with open(f, 'r', encoding='utf-8') as fp:
            content = fp.read()
        msg = extra_boost_7[base].strip()
        if "炭水化物コンボをさらに楽しむための調味料マジック" in content or \
           "美容室での「マッサージサービス」という至福の時間" in content or \
           "敬語での別れ際を彩る「お気をつけて」の心遣い" in content or \
           "相手の「大丈夫」の裏にある本音を察する「共感力」" in content or \
           "夜間の横断で命を守る反射材とライトの活用" in content or \
           "通学路に響く子供たちの元気な挨拶と地域の絆" in content or \
           "「〜ていただく」を使いこなしてビジネス敬語を極める" in content:
            continue
        if '<div class="c-vocab-box"' in content:
            parts = content.split('<div class="c-vocab-box"', 1)
            new_content = parts[0].rstrip() + "\n\n" + msg + "\n\n" + '<div class="c-vocab-box"' + parts[1]
        else:
            new_content = content.rstrip() + "\n\n" + msg + "\n"
        with open(f, 'w', encoding='utf-8') as fp:
            fp.write(new_content)
        print(f"Pushed: {base}")
