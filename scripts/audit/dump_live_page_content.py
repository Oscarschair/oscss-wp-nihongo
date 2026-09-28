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
with urllib.request.urlopen(req) as res:
    html = res.read().decode('utf-8', errors='replace')

m = re.search(r'<div class="c-entry__content[^"]*">(.*?)</div>\s*<!-- 著者プロフィール', html, re.DOTALL)
if m:
    content = m.group(1)
    print(f"Content length: {len(content)} chars")
    # 先頭500文字と末尾500文字
    print("HEAD:\n", content[:500])
    print("...")
    print("TAIL:\n", content[-500:])
else:
    print("Could not find c-entry__content")
