# -*- coding: utf-8 -*-
import glob
import os

files_map = {
    '2026-09-10-japanese-comparing-sayonara-and-matane-differences-in-goodbye-expressions.md': '相手を尊重し、心地よい距離感を保ちながら挨拶を交わすことで、毎日の生活はさらに温かく安心できるものになります。',
    '2026-09-11-kotoba-no-aya-the-trap-of-daijoubu-yes-or-no-japanese-magic-phrase.md': '相手の気持ちに寄り添い、丁寧な言葉を返すことで、お互いの信頼関係は一層深まります。'
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
        print('Finished:', b)
