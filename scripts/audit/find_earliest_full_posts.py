import glob
import re

files = glob.glob('content/posts/*.md')
files.sort()

print("=== 本文のある初期記事一覧（最古順） ===")
for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        t = fp.read()
    body = re.sub(r'---.*?---', '', t, flags=re.DOTALL)
    main_text = body.split('## 🎯 今回の語彙')[0].strip()
    if len(main_text) > 200:
        lines = [l for l in t.splitlines() if l.startswith('title:')]
        title = lines[0].replace('title:', '').strip(' "') if lines else ''
        fname = f.replace('\\', '/').split('/')[-1]
        print(f"{fname:65s} ({len(main_text):4d}字) | {title}")
