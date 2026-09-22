import glob, os, re, sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

files = sorted(glob.glob('content/posts/*.md'))
print(f"Total posts: {len(files)}")
items = []
for f in files:
    with open(f, encoding='utf-8') as fp:
        c = fp.read()
    date_m = re.search(r'date:\s*"?([^"\n]+)"?', c)
    cat_m = re.search(r'categories:\s*\n\s*-\s*"?([^"\n]+)"?', c)
    title_m = re.search(r'title:\s*"?([^"\n]+)"?', c)
    d = date_m.group(1).strip() if date_m else 'No Date'
    cat = cat_m.group(1).strip() if cat_m else 'No Cat'
    title = title_m.group(1).strip() if title_m else 'No Title'
    items.append((d[:10], cat, title, os.path.basename(f)))

items.sort(key=lambda x: x[0])
for d, cat, title, fname in items:
    print(f"{d} | {cat:<10} | {title}")
