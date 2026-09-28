import urllib.request
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

url = 'https://nihongo.oscarchair.jp/kotoba-no-aya-how-to-use-the-final-particle-yone-for-smooth-conversation/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as res:
    html = res.read().decode('utf-8', errors='replace')

h2s = re.findall(r'<h2[^>]*>.*?</h2>', html)
print(f"Total H2s: {len(h2s)}")
for h in h2s:
    print("  ", h)

# Gutenberg blocks in post_content on server
