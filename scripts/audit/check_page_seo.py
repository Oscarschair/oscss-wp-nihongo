import urllib.request
import re
import ssl
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://nihongo.oscarchair.jp/about/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8', errors='ignore')

print('=== 1. TITLE TAG ===')
m = re.search(r'<title>(.*?)</title>', html, re.I | re.S)
title = m.group(1).strip() if m else 'None'
print(f'Title: {title} ({len(title)} chars)')

print('\n=== 2. META DESCRIPTION ===')
m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.I | re.S)
desc = m.group(1).strip() if m else 'None'
print(f'Description: {desc} ({len(desc)} chars)')

print('\n=== 3. CANONICAL ===')
m = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\'](.*?)["\']', html, re.I | re.S)
canon = m.group(1).strip() if m else 'None'
print(f'Canonical: {canon}')

print('\n=== 4. OGP & TWITTER ===')
ogps = re.findall(r'<meta\s+(?:property|name)=["\'](og:[^"\']+|twitter:[^"\']+)["\']\s+content=["\'](.*?)["\']', html, re.I)
for k, v in ogps:
    print(f'{k} = {v}')

print('\n=== 5. HEADINGS HIERARCHY ===')
h1s = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.I | re.S)
print(f'h1 ({len(h1s)}):', [re.sub(r'<[^>]+>', '', x).strip() for x in h1s])
h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.I | re.S)
print(f'h2 ({len(h2s)}):', [re.sub(r'<[^>]+>', '', x).strip() for x in h2s])
h3s = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.I | re.S)
print(f'h3 ({len(h3s)}):', [re.sub(r'<[^>]+>', '', x).strip() for x in h3s])

print('\n=== 6. JSON-LD ===')
json_lds = re.findall(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', html, re.I | re.S)
for i, j in enumerate(json_lds):
    print(f'JSON-LD [{i}]:', j.strip())

print('\n=== 7. IMAGES & ALT ===')
imgs = re.findall(r'<img\s+([^>]+)>', html, re.I)
for img in imgs:
    src_m = re.search(r'src=["\'](.*?)["\']', img)
    alt_m = re.search(r'alt=["\'](.*?)["\']', img)
    src = src_m.group(1) if src_m else 'No src'
    alt = alt_m.group(1) if alt_m else 'NO ALT'
    print(f'- img: src={src}, alt={alt}')
