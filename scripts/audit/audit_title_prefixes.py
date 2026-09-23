import glob, os, re, sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

files = sorted(glob.glob('content/posts/*.md'))
results = []
for f in files:
    if os.path.getsize(f) == 0:
        continue
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    date_m = re.search(r'date:\s*"?([^"\n]+)"?', c)
    cat_m = re.search(r'categories:\s*\n\s*-\s*"?([^"\n]+)"?', c)
    title_m = re.search(r'title:\s*"?([^"\n]+)"?', c)
    d = date_m.group(1).strip() if date_m else 'No Date'
    cat = cat_m.group(1).strip() if cat_m else 'No Cat'
    title = title_m.group(1).strip() if title_m else 'No Title'
    clean_title = re.sub(r'<[^>]+>', '', title).strip()
    
    # Check if category prefix is in clean_title
    prefix_ok = any(clean_title.startswith(p) for p in ['くらべてみました：', '街角サバイバル：', 'ことばのあや：', 'カルチャーショック：'])
    results.append((d[:10], cat, prefix_ok, clean_title, os.path.basename(f)))

print(f"{'Date':<10} | {'Category':<15} | {'Prefix OK?':<10} | Title")
print("-" * 80)
missing_count = 0
for d, cat, ok, t, fname in results:
    status = "OK" if ok else "MISSING"
    if not ok:
        missing_count += 1
    print(f"{d:<10} | {cat:<15} | {status:<10} | {t[:50]} ({fname})")

print(f"\nTotal articles: {len(results)}, Missing prefix: {missing_count}")
