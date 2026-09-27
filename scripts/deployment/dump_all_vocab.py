import glob
import os
import re
import json

vocab_master = {}

for md in sorted(glob.glob('content/posts/*.md')):
    fname = os.path.basename(md)
    slug = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', fname).replace('.md', '')
    with open(md, 'r', encoding='utf-8') as f:
        text = f.read()
    
    m = re.search(r'##\s*🎯?\s*.*?(?:語彙|ボキャブラリー).*?\n(.*?)(?=\n---|\Z)', text, re.DOTALL)
    items = []
    if m:
        lines = m.group(1).split('\n')
        cur = None
        for l in lines:
            line = l.strip()
            # check word
            hm = re.search(r'^\*\s*\*\*(.+?)\*\*\s*【(?:JLPT\s*)?([Nn][1-5])】', line)
            if hm:
                if cur: items.append(cur)
                # strip ruby if any
                w = hm.group(1).strip()
                w_clean = re.sub(r'<ruby>(.*?)<rt>.*?</rt></ruby>', r'\1', w)
                cur = {'word': w_clean, 'jlpt': hm.group(2).upper(), 'meaning': '', 'example': ''}
                continue
            if cur:
                clean = re.sub(r'^\*\s*', '', line).strip()
                if '意味：' in clean or '意味:' in clean:
                    cur['meaning'] = re.sub(r'^.*?意味[：:]\s*', '', clean).strip()
                elif '例文：' in clean or '例文:' in clean:
                    cur['example'] = re.sub(r'^.*?例文[：:]\s*', '', clean).strip()
        if cur: items.append(cur)
    vocab_master[slug] = {
        'file': fname,
        'items': items
    }

with open('all_posts_vocab.json', 'w', encoding='utf-8') as f:
    json.dump(vocab_master, f, ensure_ascii=False, indent=2)

print(f"Dumped {len(vocab_master)} posts.")
