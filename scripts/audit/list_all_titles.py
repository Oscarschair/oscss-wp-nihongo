import glob
import os
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

posts = sorted(glob.glob('content/posts/*.md'))
print(f"Total posts: {len(posts)}\n")

for p in posts:
    with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
        c = fp.read()
        m_t = re.search(r'title:\s*"([^"]+)"', c)
        m_c = re.search(r'categories:\s*\n\s*-\s*"([^"]+)"', c)
        t = m_t.group(1) if m_t else os.path.basename(p)
        cat = m_c.group(1) if m_c else '不明'
        t_clean = re.sub(r'<rt>.*?</rt>', '', t)
        t_clean = re.sub(r'</?ruby>', '', t_clean)
        fname = os.path.basename(p)[:10]
        print(f"{fname} | {cat:<10} | {t_clean}")
