import glob
import os
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

top_10 = [
    "kotoba-no-aya-how-to-use-the-final-particle-yone-for-smooth-conversation",
    "kotoba-no-aya-how-to-use-the-final-particle-ne-for-a-comfortable-conversation",
    "kotoba-no-aya-how-to-use-the-final-particle-yo-for-effective-conversation",
    "japanese-comparing-sorry-excuse-me-differences-in-apology-expressions",
    "japanese-comparing-scholarships-in-japan-and-overseas-different-meaning-with-same-word",
    "japanese-comparing-interesting-and-oddy-funny-differences-in-emotional-expression",
    "culture-shock-ice-water-hospitality-in-winter-vs-hot-water-culture",
    "culture-shock-sleeping-on-the-train-japan-safety-and-inemuri-culture",
    "kotoba-no-aya-how-to-distinguish-yes-and-no-in-iidesu",
    "japanese-comparing-wakaru-and-shiru-differences-in-understanding-and-knowing"
]

all_md = glob.glob('content/posts/*.md')
print(f"{'Slug':<45} | {'目安時間':<6} | {'文字数':<6} | {'語彙BOX':<6} | {'ルビ数':<6}")
print("-" * 75)

for s in top_10:
    m = [f for f in all_md if s in f]
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
        has_box = 'c-vocab-box' in b
        ruby = len(re.findall(r'<ruby>', b))
        print(f"{s[:45]:<45} | 約{mins}分  | {chars}字 | {str(has_box):<6} | {ruby}個")
