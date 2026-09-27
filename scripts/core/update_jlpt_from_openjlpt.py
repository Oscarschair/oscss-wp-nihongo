import urllib.request
import json
import os
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_URL = "https://raw.githubusercontent.com/evanclan/OpenJLPT/main/data/json/vocab/{lvl}.json"
LEVELS = ["n5", "n4", "n3", "n2", "n1"]

os.makedirs("data/jlpt/openjlpt", exist_ok=True)

# 1. Download OpenJLPT vocab files
all_vocab = {}
level_counts = {}

for lvl in LEVELS:
    url = BASE_URL.format(lvl=lvl)
    print(f"Downloading {url} ...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    
    local_file = f"data/jlpt/openjlpt/{lvl}.json"
    with open(local_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    level_counts[lvl.upper()] = len(data)
    for entry in data:
        w = entry.get("word")
        r = entry.get("reading")
        lvl_tag = entry.get("level", lvl.upper())
        meanings = entry.get("meanings", [])
        examples = entry.get("examples", [])
        
        item = {
            "level": lvl_tag,
            "word": w,
            "reading": r,
            "meanings": meanings,
            "meaning_str": ", ".join(meanings),
            "examples": examples
        }
        
        # Key by word
        if w:
            if w not in all_vocab:
                all_vocab[w] = item
        # Key by reading if distinct and not trivial
        if r and len(r) > 1 and r != w:
            if r not in all_vocab:
                all_vocab[r] = item

print(f"\nOpenJLPT Download Complete:")
for lvl, cnt in level_counts.items():
    print(f"  {lvl}: {cnt} entries")
print(f"Total unique lookup keys: {len(all_vocab)}")

# 2. Build updated data/jlpt/jlpt_dictionary.json
output_data = {
    "source": "OpenJLPT (evanclan/OpenJLPT, CC BY-SA 4.0)",
    "summary": {
        "total_unique_keys": len(all_vocab),
        "counts_by_level": level_counts
    },
    "dictionary": all_vocab
}

dict_path = "data/jlpt/jlpt_dictionary.json"
with open(dict_path, "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"Successfully updated {dict_path} with latest OpenJLPT data!")
