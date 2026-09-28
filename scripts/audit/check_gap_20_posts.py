import glob
import os
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

short_20_slugs = [
    ("japanese-comparing-sorry-excuse-me-differences-in-apology-expressions", 1),
    ("kotoba-no-aya-how-to-use-the-final-particle-ne-for-a-comfortable-conversation", 19),
    ("japanese-comparing-scholarships-in-japan-and-overseas-different-meaning-with-same-word", 30),
    ("japanese-comparing-interesting-and-oddy-funny-differences-in-emotional-expression", 36),
    ("culture-shock-japanese-food-for-shaping-rice-find-an-authentic-chinese-restaurant", 44),
    ("kotoba-no-aya-how-to-use-the-final-particle-yo-for-effective-conversation", 85),
    ("culture-shock-ice-water-hospitality-in-winter-vs-hot-water-culture", 109),
    ("culture-shock-sleeping-on-the-train-japan-safety-and-inemuri-culture", 111),
    ("kotoba-no-aya-how-to-distinguish-yes-and-no-in-iidesu", 144),
    ("japanese-comparing-wakaru-and-shiru-differences-in-understanding-and-knowing", 150),
    ("culture-shock-carb-on-carb-combos-in-japan-ramen-fried-rice-gyoza-rice-vermicelli", 158),
    ("culture-shock-cash-on-delivery-refused-tip-keep-the-change", 161),
    ("culture-shock-haircut-price-5000-yen-vs-1000-yen-cut-hong-kong-comparison", 167),
    ("japanese-comparing-sayonara-and-matane-differences-in-goodbye-expressions", 164),
    ("street-japanese-convenience-store-register-survival-guide", 184),
    ("kotoba-no-aya-the-trap-of-daijoubu-yes-or-no-japanese-magic-phrase", 172),
    ("culture-shock-cars-stop-when-you-raise-your-hand-pedestrian-crosswalk-in-japan", 175),
    ("culture-shock-japanese-first-graders-walk-to-school-alone-safety-and-independence", 177),
    ("kotoba-no-aya-particles-zo-and-ze-anime-vs-real-life-japanese", 180),
    ("japanese-comparing-ageru-kureru-morau-differences-in-giving-and-receiving", 182)
]

all_md = glob.glob('content/posts/*.md')

print(f"{'Post ID':<8} | {'Slug':<45} | {'現状文字数':<8} | {'現状目安':<6} | {'目標(3,500字以上)'}")
print("-" * 85)

for slug, pid in short_20_slugs:
    m = [f for f in all_md if slug in f]
    if m:
        f = m[0]
        with open(f, 'r', encoding='utf-8') as fp:
            c = fp.read()
        b = re.sub(r'^---.*?---\s*', '', c, flags=re.DOTALL)
        cl = re.sub(r'<rt>.*?</rt>', '', b, flags=re.DOTALL)
        cl = re.sub(r'<[^>]+>', '', cl)
        cl = re.sub(r'\s+', '', cl)
        chars = len(cl)
        mins = (chars + 499) // 500
        print(f"ID {pid:<5} | {slug[:45]:<45} | {chars:<8}字 | 約{mins}分  | 不足: {max(0, 3600 - chars)}字")
