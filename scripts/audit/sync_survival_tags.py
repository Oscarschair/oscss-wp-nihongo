import glob, os, re, sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

files = sorted(glob.glob('content/posts/*street-*.md'))
for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    
    m = re.search(r'(tags:\s*\n)((?:\s*-\s*[^\n]+\n?)+)', c)
    if not m:
        continue
    
    header = m.group(1)
    raw_lines = [l.strip() for l in m.group(2).strip().split('\n') if l.strip()]
    tag_list = [re.sub(r'[\"\'\-]', '', l).strip() for l in raw_lines if re.sub(r'[\"\'\-]', '', l).strip()]
    
    # Ensure both '街角サバイバル' and 'サバイバル' are present
    if '街角サバイバル' not in tag_list:
        tag_list.insert(0, '街角サバイバル')
    if 'サバイバル' not in tag_list:
        idx = tag_list.index('街角サバイバル') + 1
        tag_list.insert(idx, 'サバイバル')
        
    new_tag_block = header + "\n".join([f'  - "{t}"' for t in tag_list]) + "\n"
    new_c = c[:m.start()] + new_tag_block + c[m.end():]
    
    with open(f, 'w', encoding='utf-8') as fp:
        fp.write(new_c)
    print(f"Updated {os.path.basename(f)} tags: {tag_list}")
