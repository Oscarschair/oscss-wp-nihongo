import os
import glob
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def get_pure_char_count(text):
    parts = re.split(r'^---\s*$', text, maxsplit=2, flags=re.MULTILINE)
    body = parts[2] if len(parts) >= 3 else text
    # HTMLタグ（特に <rt>...</rt>）を除去
    no_rt = re.sub(r'<rt>.*?</rt>', '', body)
    no_tags = re.sub(r'<[^>]+>', '', no_rt)
    no_links = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', no_tags)
    no_images = re.sub(r'!\[.*?\]\(.*?\)', '', no_links)
    no_md = re.sub(r'[#*`_~>\-+|]', '', no_images)
    clean = re.sub(r'\s+', '', no_md)
    return len(clean)

files = sorted(glob.glob('content/posts/*.md'))
print(f"Total posts found: {len(files)}")
print(f"{'Filename':<55} | {'Chars':>6} | {'Reading Time':>12}")
print("-" * 80)

short_posts = []
for fp in files:
    name = os.path.basename(fp)
    with open(fp, 'r', encoding='utf-8') as f:
        c = f.read()
    chars = get_pure_char_count(c)
    # 500文字/分換算
    minutes = max(1, round(chars / 500))
    print(f"{name:<55} | {chars:>6}字 | 約{minutes:>2}分")
    if minutes < 7:
        short_posts.append((fp, chars, minutes))

print("-" * 80)
print(f"Posts needing enrichment (< 7 mins / target 8-9 mins): {len(short_posts)} posts")
for p, ch, m in short_posts[:10]:
    print(f"  - {os.path.basename(p)}: {ch} chars (約{m}分)")
