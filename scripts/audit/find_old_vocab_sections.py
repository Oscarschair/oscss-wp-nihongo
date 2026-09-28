# -*- coding: utf-8 -*-
import glob
import os
import re

files = sorted(glob.glob('content/posts/*.md'))
found = []

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    
    # Strip c-vocab-box
    c_no_box = re.sub(r'<div class="c-vocab-box"[\s\S]*?</div>\s*</div>\s*</div>', '', c)
    # Strip rt and html tags
    clean_plain = re.sub(r'<rt>.*?</rt>', '', c_no_box)
    clean_plain = re.sub(r'<[^>]+>', '', clean_plain)
    if '今回の語彙' in clean_plain or '重要ボキャブラリー' in clean_plain:
        found.append((f, os.path.basename(f)))

print(f"Files with old/duplicate vocab outside c-vocab-box: {len(found)}")
for path, b in found:
    print(" ", b)
