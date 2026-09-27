import json
import sys
import re

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('all_posts_vocab.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for slug, data in d.items():
    items = data['items']
    has_issue = False
    if len(items) == 0:
        print(f"[EMPTY] {slug}")
        continue
    for it in items:
        ex = it['example']
        mean = it['meaning']
        w = it['word']
        if not ex or not mean or len(ex) < 10 or 'ビジネスの場面' in ex or re.search(r'^[#|」➔■◆▼●]|[|」]', ex) or w in ['スト', 'ました']:
            has_issue = True
            break
    if has_issue:
        print(f"[ISSUE] {slug}:")
        for it in items:
            print(f"   Word: {it['word']} [{it['jlpt']}] | Mean: {it['meaning']} | Ex: {it['example']}")
