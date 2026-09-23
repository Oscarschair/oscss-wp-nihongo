import urllib.request, re, sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

url = 'https://nihongo.oscarchair.jp/tag/%e3%82%b5%e3%83%90%e3%82%a4%e3%83%90%e3%83%ab/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='replace')
    titles = re.findall(r'class="c-card__title[^"]*">(.*?)</h3>', html, re.DOTALL)
    if not titles:
        titles = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', html, re.DOTALL)
    print("Found titles count:", len(titles))
    for t in titles[:10]:
        print(" -", re.sub(r'<[^>]+>', '', t).strip())
