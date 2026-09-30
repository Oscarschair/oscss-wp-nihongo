import glob
import re
import os

empty_slugs = [
    'japanese-comparing-wakaru-and-shiru-differences-in-understanding-and-knowing',
    'kotoba-no-aya-how-to-distinguish-yes-and-no-in-iidesu',
    'kotoba-no-aya-how-to-use-the-final-particle-yone-for-smooth-conversation',
    'culture-shock-ice-water-hospitality-in-winter-vs-hot-water-culture',
    'culture-shock-sleeping-on-the-train-japan-safety-and-inemuri-culture',
    'kotoba-no-aya-how-to-use-the-final-particle-yo-for-effective-conversation',
    'japanese-comparing-interesting-and-oddy-funny-differences-in-emotional-expression',
    'japanese-comparing-scholarships-in-japan-and-overseas-different-meaning-with-same-word',
    'kotoba-no-aya-how-to-use-the-final-particle-ne-for-a-comfortable-conversation',
    'japanese-comparing-sorry-excuse-me-differences-in-apology-expressions',
]

md_files = glob.glob('content/posts/*.md')
print(f"Total markdown files: {len(md_files)}")

mapping = {}

for f in md_files:
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    parts = re.split(r'^---\s*$', c, maxsplit=2, flags=re.MULTILINE)
    if len(parts) >= 3:
        fm = parts[1]
        slug_m = re.search(r'^slug:\s*["\']?(.*?)["\']?$', fm, re.MULTILINE)
        title_m = re.search(r'^title:\s*["\']?(.*?)["\']?$', fm, re.MULTILINE)
        slug = slug_m.group(1).strip() if slug_m else ''
        title = title_m.group(1).strip() if title_m else ''
        # strip ruby from title if any
        title = re.sub(r'<rt>.*?</rt>', '', title)
        title = re.sub(r'<rp>.*?</rp>', '', title)
        title = re.sub(r'</?ruby[^>]*>', '', title)
        title = re.sub(r'\s+', ' ', title).strip()
        
        fname = os.path.basename(f)
        if slug:
            mapping[slug] = (title, fname)
        # also match basename without date
        base_slug = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', os.path.splitext(fname)[0])
        mapping[base_slug] = (title, fname)

for s in empty_slugs:
    if s in mapping:
        print(f"MATCH: {s} -> '{mapping[s][0]}' (file: {mapping[s][1]})")
    else:
        # Partial match
        found = False
        for k in mapping:
            if s in k or k in s:
                print(f"PARTIAL MATCH: {s} -> {k} -> '{mapping[k][0]}'")
                found = True
                break
        if not found:
            print(f"NO MATCH: {s}")
