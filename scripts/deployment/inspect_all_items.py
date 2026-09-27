import json
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('all_posts_vocab.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for slug, data in d.items():
    items = data['items']
    print(f"[{slug}] (count: {len(items)})")
    for it in items:
        print(f"  - {it['word']} [{it['jlpt']}]: {it['meaning']} | EX: {it['example']}")
