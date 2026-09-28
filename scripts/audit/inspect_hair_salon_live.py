# -*- coding: utf-8 -*-
import requests
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

url = 'https://nihongo.oscarchair.jp/street-japanese-hair-salon-survival-shampoo-trap-guide/'
res = requests.get(url)
print('Status:', res.status_code)
print('Contains c-vocab-card:', 'c-vocab-card' in res.text)

# Check all occurrences of 語彙
for m in re.finditer(r'語彙', res.text):
    pos = m.start()
    print('--- MATCH AT', pos, '---')
    print(res.text[max(0, pos-100):pos+400])
    print('----------------------')
