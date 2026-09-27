import json
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open("data/jlpt/jlpt_dictionary.json", "r", encoding="utf-8") as f:
    jlpt_db = json.load(f)["dictionary"]

import sys
sys.path.append("scripts/deployment")
from apply_master_vocab import VOCAB_MASTER

print(f"Loaded JLPT dictionary with {len(jlpt_db)} entries.")

updated_count = 0
not_found = []

for slug, items in VOCAB_MASTER.items():
    for it in items:
        raw_word = it["word"]
        # extract pure word (kanji or kana)
        pure = re.sub(r'（.*?）', '', raw_word).strip()
        reading = ""
        rm = re.search(r'（(.*?)）', raw_word)
        if rm:
            reading = rm.group(1).strip()
            
        entry = None
        if pure in jlpt_db:
            entry = jlpt_db[pure]
        elif reading in jlpt_db:
            entry = jlpt_db[reading]
        elif pure.rstrip("する") in jlpt_db:
            entry = jlpt_db[pure.rstrip("する")]
            
        if entry:
            official_lvl = entry.get("level")
            official_meanings = entry.get("meanings", [])
            official_mean = entry.get("meaning_str", "")
            
            # Compare level
            if official_lvl and official_lvl != it["jlpt"]:
                print(f"[{slug}] {raw_word}: Level {it['jlpt']} -> Official {official_lvl}")
                it["jlpt"] = official_lvl
                updated_count += 1
                
            # If meaning can be enhanced or simplified
            if official_meanings and len(official_meanings) > 0:
                # keep clean first 2-3 meanings
                clean_m = ", ".join(official_meanings[:2])
                # it["meaning"] = clean_m
        else:
            not_found.append((slug, raw_word))

print(f"\nUpdated {updated_count} word levels based on OpenJLPT dictionary.")
print(f"Words not directly in standard list: {len(not_found)}")
for s, w in not_found[:15]:
    print(f"  - {w} ({s})")
