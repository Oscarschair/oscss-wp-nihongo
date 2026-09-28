import glob
import os
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

short_slugs = [
    "japanese-comparing-sorry-excuse-me-differences-in-apology-expressions",
    "kotoba-no-aya-how-to-use-the-final-particle-ne-for-a-comfortable-conversation",
    "japanese-comparing-scholarships-in-japan-and-overseas-different-meaning-with-same-word",
    "japanese-comparing-interesting-and-oddy-funny-differences-in-emotional-expression",
    "kotoba-no-aya-how-to-use-the-final-particle-yo-for-effective-conversation",
    "culture-shock-ice-water-hospitality-in-winter-vs-hot-water-culture",
    "culture-shock-sleeping-on-the-train-japan-safety-and-inemuri-culture",
    "kotoba-no-aya-how-to-use-the-final-particle-yone-for-smooth-conversation",
    "kotoba-no-aya-how-to-distinguish-yes-and-no-in-iidesu",
    "japanese-comparing-wakaru-and-shiru-differences-in-understanding-and-knowing",
    "culture-shock-carb-on-carb-combos-in-japan-ramen-fried-rice-gyoza-rice-vermicelli",
    "culture-shock-cash-on-delivery-refused-tip-keep-the-change",
    "culture-shock-haircut-price-5000-yen-vs-1000-yen-cut-hong-kong-comparison",
    "japanese-comparing-sayonara-and-matane-differences-in-goodbye-expressions",
    "street-japanese-convenience-store-register-survival-guide",
    "kotoba-no-aya-the-trap-of-daijoubu-yes-or-no-japanese-magic-phrase",
    "culture-shock-cars-stop-when-you-raise-your-hand-pedestrian-crosswalk-in-japan",
    "culture-shock-japanese-first-graders-walk-to-school-alone-safety-and-independence",
    "kotoba-no-aya-particles-zo-and-ze-anime-vs-real-life-japanese",
    "japanese-comparing-ageru-kureru-morau-differences-in-giving-and-receiving",
    "culture-shock-japanese-food-for-shaping-rice-find-an-authentic-chinese-restaurant"
]

all_md = glob.glob('content/posts/*.md')

for slug in short_slugs:
    matched = [f for f in all_md if slug in f]
    if not matched:
        print(f"[NOT FOUND] {slug}")
        continue
    f = matched[0]
    with open(f, 'r', encoding='utf-8') as fp:
        raw = fp.read()
    
    body = re.sub(r'^---.*?---\s*', '', raw, flags=re.DOTALL)
    # 文字数
    c = re.sub(r'<rt>.*?</rt>', '', body, flags=re.DOTALL)
    c = re.sub(r'<[^>]+>', '', c)
    c = re.sub(r'\s+', '', c)
    chars = len(c)
    mins = (chars + 499) // 500
    has_box = 'c-vocab-box' in body
    ruby = len(re.findall(r'<ruby>', body))
    
    print(f"{slug[:45]:<45} | {mins}分 ({chars}字) | BOX:{has_box} | ルビ:{ruby} | {os.path.basename(f)}")
