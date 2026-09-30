import urllib.request
import ssl
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://nihongo.oscarchair.jp/?sort=views'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8', errors='ignore')

articles = re.findall(r'<article[^>]*id=["\']post-(\d+)["\'][^>]*>(.*?)</article>', html, re.S)
print(f"Total cards found: {len(articles)}")

for pid, content in articles:
    title_m = re.search(r'<h3 class=["\']c-card__title["\']>(.*?)</h3>', content, re.S)
    if title_m:
        title_html = title_m.group(1).strip()
        clean = re.sub(r'<[^>]+>', '', title_html).strip()
        print(f"Post ID {pid}: title='{clean}' (raw: {repr(title_html[:80])})")
    else:
        print(f"Post ID {pid}: NO <h3 class='c-card__title'> FOUND!")
