# -*- coding: utf-8 -*-
import glob
import os
import re
import json
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('clean_master_vocab_boxes.json', 'r', encoding='utf-8') as f:
    slug_to_box = json.load(f)

files = glob.glob('content/posts/*.md')
updated = 0
already_present = 0
not_found = []

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        content = fp.read()
    
    # get slug
    slug_match = re.search(r'slug:\s*([^\s\n\r]+)', content)
    if slug_match:
        slug = slug_match.group(1).strip('"\'')
    else:
        base = os.path.basename(f)
        slug = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', base).replace('.md', '')
    
    if slug in slug_to_box:
        box_html = slug_to_box[slug].strip()
        if 'c-vocab-box' in content:
            # Check if exactly matching or update
            if box_html in content:
                already_present += 1
                continue
            # Replace old box with clean box
            new_content = re.sub(r'<div class="c-vocab-box".*?</div>\s*</div>\s*</div>', box_html, content, flags=re.DOTALL)
            if new_content == content:
                # regex didn't match standard closing, replace greedily
                new_content = re.sub(r'<div class="c-vocab-box".*', box_html, content, flags=re.DOTALL)
            with open(f, 'w', encoding='utf-8') as fp:
                fp.write(new_content.rstrip() + '\n')
            updated += 1
        else:
            # Append clean box
            new_content = content.rstrip() + '\n\n' + box_html + '\n'
            with open(f, 'w', encoding='utf-8') as fp:
                fp.write(new_content)
            updated += 1
    else:
        not_found.append((os.path.basename(f), slug))

print(f"Updated/Injected vocab boxes into {updated} markdown files.")
print(f"Already accurately present: {already_present} files.")
if not_found:
    print(f"Not found in master json ({len(not_found)} files):")
    for fname, sl in not_found:
        print(f"  {fname} -> {sl}")
