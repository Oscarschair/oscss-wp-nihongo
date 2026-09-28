import glob
import re
import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

slugs = [
    "japanese-comparing-sorry-excuse-me-differences-in-apology-expressions",
    "japanese-comparing-scholarships-in-japan-and-overseas-different-meaning-with-same-word",
    "japanese-comparing-interesting-and-oddy-funny-differences-in-emotional-expression",
    "culture-shock-ice-water-hospitality-in-winter-vs-hot-water-culture",
    "culture-shock-sleeping-on-the-train-japan-safety-and-inemuri-culture",
    "kotoba-no-aya-how-to-distinguish-yes-and-no-in-iidesu",
    "japanese-comparing-wakaru-and-shiru-differences-in-understanding-and-knowing"
]

all_md = glob.glob('content/posts/*.md')
for s in slugs:
    m = [f for f in all_md if s in f]
    if m:
        f = m[0]
        with open(f, 'r', encoding='utf-8') as fp:
            c = fp.read()
        print(f"=== {s} ({os.path.basename(f)}) ===")
        print(c[:400])
        print("...\n")
