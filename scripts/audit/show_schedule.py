import glob, os, re, sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

files = sorted(glob.glob('content/posts/*.md'))
posts = []
for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    date_m = re.search(r'date:\s*"?([^"\n]+)"?', c)
    cat_m = re.search(r'categories:\s*\n\s*-\s*"?([^"\n]+)"?', c)
    title_m = re.search(r'title:\s*"?([^"\n]+)"?', c)
    d = date_m.group(1).strip() if date_m else 'No Date'
    cat = cat_m.group(1).strip() if cat_m else 'No Cat'
    title = title_m.group(1).strip() if title_m else 'No Title'
    clean_title = re.sub(r'<[^>]+>', '', title).strip()
    posts.append((d[:10], cat, clean_title, os.path.basename(f)))

posts.sort(key=lambda x: x[0])
today = '2026-09-23'

print("=== [現在公開中] ===")
for d, cat, title, fname in posts:
    if d <= today:
        print(f"{d} | {cat:<12} | {title}")

print("\n=== [この後（予約・ストック済みの記事）] ===")
for d, cat, title, fname in posts:
    if d > today:
        print(f"{d} | {cat:<12} | {title}")
