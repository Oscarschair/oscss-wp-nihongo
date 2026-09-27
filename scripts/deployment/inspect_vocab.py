import json
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('vocab_summary.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for fpath, items in list(d.items()):
    print('=== ' + fpath + ' ===')
    for it in items:
        print(f"  Word: {it['word']} [{it['jlpt']}]")
        print(f"  Mean: {it['meaning']}")
        print(f"  Exam: {it['example']}")
