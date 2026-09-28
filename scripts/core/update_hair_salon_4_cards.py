# -*- coding: utf-8 -*-
import json
import re

with open('clean_master_vocab_boxes.json', 'r', encoding='utf-8') as f:
    vb = json.load(f)

box_4 = """<div class="c-vocab-box">
  <h3 class="c-vocab-box__title">🎯 今回の語彙（重要ボキャブラリー）</h3>
  <p class="c-vocab-box__lead">この学習ノートに登場した、覚えておきたい重要日本語：</p>
  <div class="c-vocab-grid">
    <div class="c-vocab-card">
      <div class="c-vocab-card__header">
        <span class="c-vocab-card__word">痒い（かゆい）</span>
        <span class="c-badge c-badge--jlpt c-badge--jlpt-n1">JLPT N1</span>
      </div>
      <p class="c-vocab-card__meaning"><strong>意味：</strong>itchy</p>
      <p class="c-vocab-card__example"><strong>例文：</strong>シャンプーのときに「痒いところはありませんか」と尋ねられた。</p>
    </div>
    <div class="c-vocab-card">
      <div class="c-vocab-card__header">
        <span class="c-vocab-card__word">流す（ながす）</span>
        <span class="c-badge c-badge--jlpt c-badge--jlpt-n3">JLPT N3</span>
      </div>
      <p class="c-vocab-card__meaning"><strong>意味：</strong>to rinse, to wash away</p>
      <p class="c-vocab-card__example"><strong>例文：</strong>泡が髪に残らないように、シャワーのお湯でしっかり流す。</p>
    </div>
    <div class="c-vocab-card">
      <div class="c-vocab-card__header">
        <span class="c-vocab-card__word">指名（しめい）</span>
        <span class="c-badge c-badge--jlpt c-badge--jlpt-n2">JLPT N2</span>
      </div>
      <p class="c-vocab-card__meaning"><strong>意味：</strong>nomination, designation</p>
      <p class="c-vocab-card__example"><strong>例文：</strong>いつも丁寧にカットしてくれるお気に入りの美容師さんを指名する。</p>
    </div>
    <div class="c-vocab-card">
      <div class="c-vocab-card__header">
        <span class="c-vocab-card__word">梳く（すく）</span>
        <span class="c-badge c-badge--jlpt c-badge--jlpt-n2">JLPT N2</span>
      </div>
      <p class="c-vocab-card__meaning"><strong>意味：</strong>to thin out (hair)</p>
      <p class="c-vocab-card__example"><strong>例文：</strong>髪の長さを変えずに、毛量だけを軽くするためにすいてもらった。</p>
    </div>
  </div>
</div>"""

vb['street-japanese-hair-salon-survival-shampoo-trap-guide'] = box_4

with open('clean_master_vocab_boxes.json', 'w', encoding='utf-8') as f:
    json.dump(vb, f, ensure_ascii=False, indent=2)

# Update local markdown
md_path = 'content/posts/2026-09-11-street-japanese-hair-salon-survival-shampoo-trap-guide.md'
with open(md_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace c-vocab-box
new_content = re.sub(r'<div class="c-vocab-box"[\s\S]*?</div>\s*</div>\s*</div>', box_4, content)
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated 4-card vocab box in clean_master_vocab_boxes.json and markdown file!")
