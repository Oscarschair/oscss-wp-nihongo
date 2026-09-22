import urllib.request
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import time
# 1. トップページから公開済み記事のURLを取得
ts = str(int(time.time()))
home_url = f'https://nihongo.oscarchair.jp/?nocache={ts}'
req = urllib.request.Request(home_url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
home_html = urllib.request.urlopen(req).read().decode('utf-8')

print('=== 1. CARD TITLE IN HOME (Top Page) ===')
cards = re.findall(r'<h3 class="c-card__title">[\s\S]*?<a[^>]+href="([^"]+)"[^>]*>([\s\S]*?)</a>', home_html)
if cards:
    first_url, first_card_title = cards[0]
    print(f"URL: {first_url}")
    print(f"Card Title HTML:\n{first_card_title.strip()}")
else:
    print("No cards found on home page")
    first_url = None

if first_url:
    print('\n=== 2. SINGLE POST INSPECTION ===')
    post_req = urllib.request.Request(first_url + f'?nocache={ts}', headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
    post_html = urllib.request.urlopen(post_req).read().decode('utf-8')

    print('\n[TITLE TAG (Browser Tab)]')
    m = re.search(r'<title>(.*?)</title>', post_html)
    print(m.group(1) if m else 'NOT FOUND')

    print('\n[META DESCRIPTION (SEO)]')
    m = re.search(r'<meta name="description" content="(.*?)"', post_html)
    print(m.group(1) if m else 'NOT FOUND')

    print('\n[OG TITLE (Social Share)]')
    m = re.search(r'<meta property="og:title" content="(.*?)"', post_html)
    print(m.group(1) if m else 'NOT FOUND')

    print('\n[H1 ENTRY TITLE (UI Heading)]')
    m = re.search(r'<h1 class="c-entry__title">(.*?)</h1>', post_html, re.DOTALL)
    print(m.group(1).strip() if m else 'NOT FOUND')

    print('\n[RUBY BADGE IN META]')
    m = re.search(r'<span class="c-entry__badge c-entry__badge--furigana"[^>]*>(.*?)</span>', post_html)
    print(m.group(0) if m else 'NOT FOUND')

    print('\n[BREADCRUMB TITLE]')
    m = re.search(r'<li class="c-breadcrumb__item c-breadcrumb__item--current"[^>]*><span itemprop="name">(.*?)</span>', post_html)
    print(m.group(1) if m else 'NOT FOUND')
