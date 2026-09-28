# -*- coding: utf-8 -*-
import glob
import os

files_map = {
    '2026-09-09-culture-shock-carb-on-carb-combos-in-japan-ramen-fried-rice-gyoza-rice-vermicelli.md': '日本の食文化の奥深さと、働く人々の活力を支える温かい定食屋の魅力を、ぜひお腹いっぱい味わってみてくださいね！ これからも様々な日本の美味しい食文化を体験して、元気いっぱいに毎日を過ごしていきましょう！',
    '2026-09-10-culture-shock-haircut-price-5000-yen-vs-1000-yen-cut-hong-kong-comparison.md': '自分のライフスタイルや予算に合わせて賢くサロンを使い分け、日本での快適で清潔感あふれる毎日を思いっきり楽しんでいきましょう！ 素敵なヘアスタイルで、新しい一日を笑顔でスタートさせてくださいね！',
    '2026-09-10-japanese-comparing-sayonara-and-matane-differences-in-goodbye-expressions.md': '相手を思いやる別れ際の言葉一つで、明日からの人間関係は驚くほど心地よく円滑になります。自信を持って笑顔で挨拶を交わしていきましょう！ 心からの「またね！」が、きっと次の素敵な出会いを連れてきてくれます。',
    '2026-09-11-kotoba-no-aya-the-trap-of-daijoubu-yes-or-no-japanese-magic-phrase.md': '言葉の奥にある相手への配慮や優しさを感じ取りながら、自分からも具体的な言葉を添えて返すことで、より深い信頼関係を築いていきましょう！ お互いを気遣う温かい対話が、あなたの日本生活をより一層豊かなものにしてくれます。'
}

for f in glob.glob('content/posts/*.md'):
    b = os.path.basename(f)
    if b in files_map:
        with open(f, 'r', encoding='utf-8') as fp:
            c = fp.read()
        p = c.split('<div class="c-vocab-box"', 1)
        nc = p[0].rstrip() + '\n\n' + files_map[b] + '\n\n<div class="c-vocab-box"' + p[1]
        with open(f, 'w', encoding='utf-8') as fp:
            fp.write(nc)
        print('Topped up:', b)
