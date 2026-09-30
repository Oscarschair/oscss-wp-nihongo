import urllib.request
import ssl
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request('https://nihongo.oscarchair.jp/about/', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8', errors='ignore')

opens = len(re.findall(r'<div[^>]*class=["\'][^"\']*c-no-ads', html))
print(f'c-no-ads open divs: {opens}')

has_anno = 'google-anno-skip' in html
has_noab = 'adsbygoogle-noablate' in html
has_data_skip = 'data-google-anno-skip="true"' in html
has_data_exclude = 'data-ad-exclude="true"' in html

print(f'google-anno-skip: {has_anno}')
print(f'adsbygoogle-noablate: {has_noab}')
print(f'data-google-anno-skip: {has_data_skip}')
print(f'data-ad-exclude: {has_data_exclude}')
