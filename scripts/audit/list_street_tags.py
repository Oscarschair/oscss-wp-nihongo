import glob, os, re, sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

files = sorted(glob.glob('content/posts/*street-*.md'))
for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    m = re.search(r'tags:\s*\n((?:\s*-\s*[^\n]+\n?)+)', c)
    if m:
        raw_tags = m.group(1).strip().split('\n')
        tags = [re.sub(r'[\"\'\-]', '', l).strip() for l in raw_tags]
        print(os.path.basename(f), tags)
