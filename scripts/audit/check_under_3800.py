# -*- coding: utf-8 -*-
import glob
import os
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

files = glob.glob('content/posts/*.md')
under_target = []

for f in sorted(files):
    with open(f, 'r', encoding='utf-8') as fp:
        text = fp.read()
    body = re.sub(r'^---.*?---\s*', '', text, flags=re.DOTALL)
    # ルビやHTMLタグは文字数カウントから除去（WordPress側 oscss_get_reading_time と同一基準）
    clean = re.sub(r'<rt>.*?</rt>', '', body)
    clean = re.sub(r'<[^>]+>', '', clean)
    clean = re.sub(r'\s+', '', clean)
    chars = len(clean)
    mins = (chars + 499) // 500
    base = os.path.basename(f)
    if chars < 3800:
        under_target.append((f, base, chars, mins, 3800 - chars))

print(f"=== 3,800文字（目安8〜9分）未満の記事: {len(under_target)} 件 ===")
for path, base, chars, mins, gap in under_target:
    print(f"約{mins}分 ({chars}字 / 不足 {gap}字) : {base}")
