import glob
import os
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

files = sorted(glob.glob('content/posts/*.md'))

print(f"{'Filename':<55} | {'Chars':<6} | {'Minutes (500c/m)':<15}")
print("-" * 80)

for f in files:
    fname = os.path.basename(f)
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    # Strip frontmatter
    c_no_fm = re.sub(r'^---.*?---\s*', '', c, flags=re.DOTALL)
    # Strip markdown syntax and tags
    clean = re.sub(r'<[^>]+>', '', c_no_fm)
    clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean)
    clean = re.sub(r'[#*`_~>\-|]', '', clean)
    clean = re.sub(r'\s+', '', clean)
    char_count = len(clean)
    minutes = max(1, (char_count + 499) // 500)
    print(f"{fname:<55} | {char_count:<6} | 約{minutes}分")
