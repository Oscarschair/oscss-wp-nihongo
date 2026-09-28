# -*- coding: utf-8 -*-
import json
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('clean_master_vocab_boxes.json', 'r', encoding='utf-8') as f:
    vb = json.load(f)

for k, v in vb.items():
    if '痒い' in v or '梳く' in v or 'シャンプー' in v or 'hair-salon' in k or 'haircut' in k:
        print('KEY:', k)
        print(v)
        print('='*50)
