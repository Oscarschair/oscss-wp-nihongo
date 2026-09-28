import urllib.request
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

url = 'https://nihongo.oscarchair.jp/street-japanese-station-ticket-gate-dungeon-guide/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as res:
        html = res.read().decode('utf-8', errors='replace')

    sections = re.findall(r'<section[^>]*class=["\'][^"\']*c-entry__section[^"\']*["\'][^>]*>', html)
    print(f"Total c-entry__section found in HTML: {len(sections)}")
    for s in sections[:6]:
        print("  ", s)

    has_ads = bool(re.search(r'<section[^>]*class=["\'][^"\']*c-entry__section.*?<ins\b', html, re.DOTALL))
    print(f"Any ads inside section: {has_ads}")
except Exception as e:
    print("Error:", e)
