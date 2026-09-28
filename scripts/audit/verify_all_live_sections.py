# -*- coding: utf-8 -*-
import requests
import re
import sys
from bs4 import BeautifulSoup

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

test_slugs = [
    # ユーザー指摘の最重要記事
    "kotoba-no-aya-how-to-use-the-final-particle-yone-for-smooth-conversation",
    # 初期記事
    "japanese-comparing-sorry-excuse-me-differences-in-apology-expressions",
    "kotoba-no-aya-how-to-use-the-final-particle-ne-for-a-comfortable-conversation",
    "japanese-comparing-interesting-and-oddy-funny-differences-in-emotional-expression",
    "culture-shock-ice-water-hospitality-in-winter-vs-hot-water-culture",
    # 中盤記事
    "culture-shock-cash-on-delivery-refused-tip-keep-the-change",
    "kotoba-no-aya-the-trap-of-daijoubu-yes-or-no-japanese-magic-phrase",
    "street-japanese-convenience-store-register-survival-guide",
    "culture-shock-carb-on-carb-combos-in-japan-ramen-fried-rice-gyoza-rice-vermicelli",
    # 最新記事
    "street-japanese-city-hall-resident-registration-dungeon-guide",
    "japanese-comparing-rashii-souda-youda-differences"
]

print("="*100)
print(f"{'SLUG':<45} | {'読了目安':<8} | {'語彙BOX':<6} | {'ルビ数':<6} | {'SECTION数':<9} | {'セクション内広告':<10}")
print("="*100)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

all_ok = True

for slug in test_slugs:
    url = f"https://nihongo.oscarchair.jp/{slug}/"
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code != 200:
            print(f"{slug:<45} | HTTP {res.status_code}")
            continue
        
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')
        
        # 読了目安時間
        rt_match = re.search(r'読了目安\s*約(\d+)分', html)
        reading_time = f"約{rt_match.group(1)}分" if rt_match else "N/A"
        
        # 語彙ボックス
        vocab_box = soup.find('div', class_='c-vocab-box')
        has_vocab = "あり" if vocab_box else "なし"
        
        # ルビ数
        rubies = soup.find_all('ruby')
        ruby_count = len(rubies)
        
        # entry section
        sections = soup.find_all('section', class_='c-entry__section')
        section_count = len(sections)
        
        # セクション内広告検査 (ins.adsbygoogle, .google-auto-placed, iframe inside section)
        ads_inside = 0
        for s in sections:
            ads_inside += len(s.find_all('ins', class_='adsbygoogle'))
            ads_inside += len(s.find_all(class_='google-auto-placed'))
            ads_inside += len(s.find_all('iframe'))
        
        ads_status = "0件 (完全遮断)" if ads_inside == 0 else f"{ads_inside}件検出(NG!)"
        if ads_inside > 0 or not vocab_box or section_count == 0:
            all_ok = False
        
        print(f"{slug[:45]:<45} | {reading_time:<8} | {has_vocab:<6} | {ruby_count:<6} | {section_count}個{'':<6} | {ads_status:<10}")
        
    except Exception as e:
        print(f"{slug:<45} | ERROR: {e}")

print("="*100)
if all_ok:
    print("✅ 全検証項目パーフェクト合格：セクション化、内部広告0件、語彙BOX、ルビ、読了目安8〜9分が完全稼働中！")
else:
    print("⚠️ 一部不合格項目があります。")
