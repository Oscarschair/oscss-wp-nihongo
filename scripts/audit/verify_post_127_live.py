import urllib.request
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import time
timestamp = int(time.time())
url = f'https://nihongo.oscarchair.jp/kotoba-no-aya-how-to-use-the-final-particle-yone-for-smooth-conversation/?nocache={timestamp}'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache'
})
try:
    with urllib.request.urlopen(req) as res:
        html = res.read().decode('utf-8', errors='replace')

    # 読了時間表示の確認
    rt_m = re.search(r'読了目安\s*約(\d+)分', html)
    print("Reading time on page:", rt_m.group(0) if rt_m else "NOT FOUND")

    # 語彙ボックスの確認
    has_vocab = 'c-vocab-box' in html
    print("Vocab box on page:", has_vocab)

    # ルビの確認
    ruby_count = len(re.findall(r'<ruby>', html))
    print("Ruby tags on page:", ruby_count)

    # セクションタグの確認
    sections = re.findall(r'<section[^>]*class=["\'][^"\']*c-entry__section[^"\']*["\'][^>]*>', html)
    print(f"Total c-entry__section found: {len(sections)}")
    for s in sections[:6]:
        print("  ", s)

    # セクション内の広告有無
    has_ads = bool(re.search(r'<section[^>]*class=["\'][^"\']*c-entry__section.*?<ins\b', html, re.DOTALL))
    print(f"Any ads inside section: {has_ads}")

except Exception as e:
    print("Error:", e)
