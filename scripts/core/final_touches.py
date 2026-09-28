# -*- coding: utf-8 -*-
import os
import sys
import glob

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

final_touches = {
    "2026-09-06-japanese-comparing-wakaru-and-shiru-differences-in-understanding-and-knowing.md": """
### 💡 編集部からのまとめメッセージ
言葉の意味を頭で覚えるだけでなく、相手との関係性や心理的距離に応じて言葉を選べるようになることこそが、生きた語学学習の醍醐味です。「わかる」の持つ共感の力と、「知る」の持つ客観的な事実の力を使い分け、より豊かなコミュニケーションを築いていきましょう！
""",

    "2026-09-09-culture-shock-carb-on-carb-combos-in-japan-ramen-fried-rice-gyoza-rice-vermicelli.md": """
### 💡 編集部からのまとめメッセージ：日本の「炭水化物愛」を受け止めて
異国の食文化に出会った時、「ありえない！」と拒絶するのではなく、「なぜこの組み合わせが生まれたのだろう？」と歴史や人々の生活背景に思いを馳せてみると、世界が一段と広がります。日本の忙しい労働者を支えてきたエネルギーの結晶、炭水化物コンボを、ぜひ一度はお腹を空かせて豪快に味わってみてくださいね！
""",

    "2026-09-10-culture-shock-haircut-price-5000-yen-vs-1000-yen-cut-hong-kong-comparison.md": """
### 💡 編集部からのまとめメッセージ：日本のサロン文化の楽しみ方
1,000円カットの無駄を極限まで削ぎ落とした「機能美」と、サロンの至れり尽くせりの「贅沢な癒やし」。どちらも世界に誇る日本の素晴らしいサービス産業の形です。旅行中や忙しい日常の中で、自分の気分やスケジュールに合わせてこの2つの世界を自由に使い分けられるようになれば、あなたも立派な日本生活の達人です！
""",

    "2026-09-10-japanese-comparing-sayonara-and-matane-differences-in-goodbye-expressions.md": """
### 💡 編集部からのまとめメッセージ：言葉は再会の約束
「さようなら」に宿る別れの重みを知ることで、日常の「またね！」「お疲れ様でした！」という何気ない挨拶の温かさがより一層身に染みて感じられるはずです。人と人との繋がりを大切にする日本の挨拶文化を、毎日の出会いと別れの瞬間の中でぜひ楽しんで使ってみてください！
""",

    "2026-09-11-kotoba-no-aya-the-trap-of-daijoubu-yes-or-no-japanese-magic-phrase.md": """
### 💡 編集部からのまとめメッセージ：曖昧さを乗り越えるコミュニケーション
「大丈夫」という言葉の多面性は、相手への気遣いや調和を最優先にする日本社会の鏡でもあります。単語一つの意味に縛られるのではなく、前後の文脈や相手の表情、仕草といったノンバーバル（非言語）コミュニケーションを感じ取る練習を重ねて、より深い対話の喜びを体感してください！
""",

    "2026-09-12-culture-shock-cars-stop-when-you-raise-your-hand-pedestrian-crosswalk-in-japan.md": """
### 💡 編集部からのまとめメッセージ：思いやりの連鎖が街を作る
横断歩道で手を上げる行為、そしてそれに応えて止まってくれるドライバーのブレーキ。この日常の小さなやり取りの中には、世界が賞賛する日本の相互信頼の精神が息づいています。お互いへの感謝の会釈一つで、街の空気はもっと優しくなります。日本を訪れた際は、ぜひ笑顔で手を挙げてみてくださいね！
""",

    "2026-09-13-culture-shock-japanese-first-graders-walk-to-school-alone-safety-and-independence.md": """
### 💡 編集部からのまとめメッセージ：小さな一歩を社会全体で育てる
小さな体で大きなランドセルを背負い、一生懸命に前を向いて歩く小学生たちの姿は、自立の尊さとそれを温かく見守る日本社会の包容力を象徴しています。安全とは誰か一人が作るものではなく、地域の人々のまなざしの積み重ねによって守られているということを、彼らの登下校の風景が教えてくれます。
""",

    "2026-09-14-kotoba-no-aya-particles-zo-and-ze-anime-vs-real-life-japanese.md": """
### 💡 編集部からのまとめメッセージ：表現の引き出しを豊かに
アニメや漫画の日本語は、感情をダイナミックに表現するための素晴らしいエンターテインメントです。現実のリアルな日常会話との境界線を理解した上で使い分けられるようになれば、日本語のニュアンスのグラデーションを自由自在に操る楽しさを味わえるはずです！
""",

    "2026-09-15-japanese-comparing-ageru-kureru-morau-differences-in-giving-and-receiving.md": """
### 💡 編集部からのまとめメッセージ：思いやりのベクトルを意識して
授受表現（あげる・くれる・もらう）は、日本語の中でも最も美しく、相手との絆や感謝の距離感を繊細に映し出す鏡です。主語と矢印の向きを意識するだけで、相手を思いやる自然な敬語や気配りが自然と口から出てくるようになります。自信を持って使っていきましょう！
"""
}

files = glob.glob('content/posts/*.md')
updated = 0

for f in files:
    base = os.path.basename(f)
    if base in final_touches:
        with open(f, 'r', encoding='utf-8') as fp:
            content = fp.read()
        
        msg = final_touches[base].strip()
        
        if "編集部からのまとめメッセージ" in content:
            continue
        
        if '<div class="c-vocab-box"' in content:
            parts = content.split('<div class="c-vocab-box"', 1)
            new_content = parts[0].rstrip() + "\n\n" + msg + "\n\n" + '<div class="c-vocab-box"' + parts[1]
        else:
            new_content = content.rstrip() + "\n\n" + msg + "\n"
        
        with open(f, 'w', encoding='utf-8') as fp:
            fp.write(new_content)
        updated += 1
        print(f"Added final touch: {base}")

print(f"Updated {updated} files.")
