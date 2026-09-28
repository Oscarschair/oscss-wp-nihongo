import glob
import re
import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

slugs = [
    "culture-shock-carb-on-carb-combos-in-japan-ramen-fried-rice-gyoza-rice-vermicelli",
    "culture-shock-cash-on-delivery-refused-tip-keep-the-change",
    "culture-shock-haircut-price-5000-yen-vs-1000-yen-cut-hong-kong-comparison",
    "japanese-comparing-sayonara-and-matane-differences-in-goodbye-expressions",
    "street-japanese-convenience-store-register-survival-guide",
    "kotoba-no-aya-the-trap-of-daijoubu-yes-or-no-japanese-magic-phrase",
    "culture-shock-cars-stop-when-you-raise-your-hand-pedestrian-crosswalk-in-japan",
    "culture-shock-japanese-first-graders-walk-to-school-alone-safety-and-independence",
    "kotoba-no-aya-particles-zo-and-ze-anime-vs-real-life-japanese",
    "japanese-comparing-ageru-kureru-morau-differences-in-giving-and-receiving"
]

all_md = glob.glob('content/posts/*.md')
for s in slugs:
    m = [f for f in all_md if s in f]
    if m:
        f = m[0]
        with open(f, 'r', encoding='utf-8') as fp:
            c = fp.read()
        print(f"=== {s} ({os.path.basename(f)}) ===")
        print(c[:300])
        print("...\n")
