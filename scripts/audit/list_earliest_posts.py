import glob
import re

files = glob.glob('content/posts/*.md')
files.sort()

print("=== 最古順の初期記事一覧 ===")
for f in files[:10]:
    with open(f, 'r', encoding='utf-8') as fp:
        lines = [fp.readline() for _ in range(15)]
    title = ""
    for l in lines:
        if l.startswith('title:'):
            title = l.replace('title:', '').strip(' "\n')
            break
    fname = f.replace('\\', '/').split('/')[-1]
    print(f"{fname:75s} | {title}")
