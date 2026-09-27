import glob
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

dirty_records = []

for f in sorted(glob.glob('content/posts/*.md')):
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    
    # find vocab section
    match = re.search(r'##\s*🎯?\s*.*?(?:語彙|ボキャブラリー).*?\n(.*?)(?=\n---|\Z)', c, re.DOTALL)
    if not match:
        continue
    
    lines = match.group(1).split('\n')
    current_word = None
    for line in lines:
        line_str = line.strip()
        header_m = re.search(r'^\*\s*\*\*(.+?)\*\*', line_str)
        if header_m:
            current_word = header_m.group(1)
            continue
        
        ex_m = re.search(r'^[*\-\s]*例文[：:](.*)', line_str)
        if ex_m and current_word:
            ex_val = ex_m.group(1).strip()
            # Check if it looks bad: contains markdown headings, table bars, or starts with weird quotes/symbols or is an explanation
            if any(bad in ex_val for bad in ['##', '|', '」', '│', '➔', '**', '説明：']) or ex_val.startswith(('・', '※', '【', '1.', '2.', '3.')):
                dirty_records.append((f, current_word, ex_val))

print(f"Total dirty examples found: {len(dirty_records)}")
for f, w, ex in dirty_records:
    print(f"File: {f}")
    print(f"  Word: {w}")
    print(f"  Ex:   {ex}")
    print("-" * 50)
