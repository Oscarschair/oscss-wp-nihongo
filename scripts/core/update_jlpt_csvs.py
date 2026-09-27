import urllib.request
import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CSV_URL = "https://raw.githubusercontent.com/evanclan/OpenJLPT/main/data/csv/vocab-{lvl}.csv"
LEVELS = ["n5", "n4", "n3", "n2", "n1"]

for lvl in LEVELS:
    url = CSV_URL.format(lvl=lvl)
    print(f"Downloading CSV {url} ...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode('utf-8')
    
    out_path = f"data/jlpt/{lvl}.csv"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Saved {out_path}")

print("All JLPT CSV files updated successfully!")
