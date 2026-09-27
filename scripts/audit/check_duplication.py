import glob
import os
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

keywords = ['承知', '了解', 'かしこまり', '市役所', '区役所', '住民票', '転入', '在留', 'ていく', 'てくる']

posts = sorted(glob.glob('content/posts/*.md'))
print(f"Total markdown posts: {len(posts)}")

matched_summary = []

for p in posts:
    with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
        c = fp.read()
        title_m = re.search(r'title:\s*"([^"]+)"', c)
        title = title_m.group(1) if title_m else os.path.basename(p)
        title_clean = re.sub(r'<rt>.*?</rt>', '', title)
        title_clean = re.sub(r'</?ruby>', '', title_clean)
        
        matches = [k for k in keywords if k in title_clean]
        body_matches = [k for k in keywords if k in c]
        
        if matches:
            matched_summary.append((p, title_clean, matches, 'TITLE'))
        elif body_matches:
            # check if it's just incidental or significant
            matched_summary.append((p, title_clean, body_matches, 'BODY'))

print("\n=== タイトルにキーワードを含む記事 ===")
for p, t, m, loc in matched_summary:
    if loc == 'TITLE':
        print(f"[{m}] {t} ({os.path.basename(p)})")

print("\n=== 本文中に言及がある記事（参考） ===")
for p, t, m, loc in matched_summary:
    if loc == 'BODY':
        print(f"[{','.join(m)}] {t}")
