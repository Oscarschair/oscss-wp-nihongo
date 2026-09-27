import json
import re
import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.append("scripts/deployment")
from apply_master_vocab import VOCAB_MASTER, generate_vocab_box_html, generate_vocab_markdown

# Load OpenJLPT dictionary
with open("data/jlpt/jlpt_dictionary.json", "r", encoding="utf-8") as f:
    jlpt_db = json.load(f)["dictionary"]

# Official standards mapping for words that are compounds or variants
OFFICIAL_MANUAL_MAP = {
    "謝罪（しゃざい）": {"lvl": "N1", "meaning": "apology"},
    "失礼（しつれい）": {"lvl": "N5", "meaning": "discourtesy, excuse me"},
    "相槌（あいづち）": {"lvl": "N1", "meaning": "chiming in, nodding along"},
    "本格的（ほんかくてき）": {"lvl": "N2", "meaning": "authentic, genuine"},
    "お冷（おひや）": {"lvl": "N2", "meaning": "cold drinking water"},
    "もてなし（もてなし）": {"lvl": "N1", "meaning": "hospitality, reception"},
    "貴重品（きちょうひん）": {"lvl": "N2", "meaning": "valuables"},
    "共有（きょうゆう）": {"lvl": "N1", "meaning": "sharing"},
    "炭水化物（たんすいかぶつ）": {"lvl": "N1", "meaning": "carbohydrate"},
    "満腹（まんぷく）": {"lvl": "N2", "meaning": "full stomach"},
    "代引き（だいびき）": {"lvl": "N2", "meaning": "cash on delivery"},
    "心付け（こころづけ）": {"lvl": "N1", "meaning": "tip, gratuity"},
    "美容院（びよういん）": {"lvl": "N3", "meaning": "beauty salon, hair salon"},
    "散髪（さんぱつ）": {"lvl": "N2", "meaning": "haircut"},
    "接客（せっきゃく）": {"lvl": "N1", "meaning": "customer service"},
    "レジ袋（レジぶくろ）": {"lvl": "N3", "meaning": "plastic shopping bag"},
    "温め（あたため）": {"lvl": "N3", "meaning": "heating up"},
    "横断歩道（おうだんほどう）": {"lvl": "N3", "meaning": "pedestrian crossing"},
    "一時停止（いちじていし）": {"lvl": "N2", "meaning": "temporary stop"},
    "語尾（ごび）": {"lvl": "N2", "meaning": "word ending"},
    "お通し（おとおし）": {"lvl": "N2", "meaning": "table appetizer"},
    "呼びかけ（よびかけ）": {"lvl": "N2", "meaning": "calling out"},
    "ゴミ箱（ごみばこ）": {"lvl": "N4", "meaning": "trash can"},
    "美化（びか）": {"lvl": "N1", "meaning": "beautification"},
    "少々（しょうしょう）": {"lvl": "N3", "meaning": "a little, just a minute"},
    "湯船（ゆぶね）": {"lvl": "N2", "meaning": "bathtub"},
    "脱衣所（だついじょ）": {"lvl": "N2", "meaning": "dressing room"},
    "消音（しょうおん）": {"lvl": "N1", "meaning": "muting, sound suppression"},
    "羞恥心（しゅうちしん）": {"lvl": "N1", "meaning": "sense of shame"},
    "節水（せっすい）": {"lvl": "N1", "meaning": "saving water"},
    "謙遜（けんそん）": {"lvl": "N2", "meaning": "modesty, humility"},
    "心配り（こころくばり）": {"lvl": "N1", "meaning": "thoughtfulness"},
    "傘立て（かさたて）": {"lvl": "N3", "meaning": "umbrella stand"},
    "ビニール袋（ビニールぶくろ）": {"lvl": "N3", "meaning": "plastic bag"},
    "席取り（せきとり）": {"lvl": "N2", "meaning": "securing a seat"},
    "特急（とっきゅう）": {"lvl": "N4", "meaning": "express train / lane"},
    "お会計（おかいけい）": {"lvl": "N3", "meaning": "bill, check"},
    "食券（しょっけん）": {"lvl": "N3", "meaning": "meal ticket"},
    "コール（コール）": {"lvl": "N2", "meaning": "ordering call"},
    "お疲れ様（おつかれさま）": {"lvl": "N3", "meaning": "thank you for your hard work"},
    "マナーモード（マナーモード）": {"lvl": "N3", "meaning": "silent mode"},
    "不在票（ふざいひょう）": {"lvl": "N2", "meaning": "delivery notice"},
    "再配達（さいはいたつ）": {"lvl": "N2", "meaning": "redelivery"},
    "結構です（けっこうです）": {"lvl": "N3", "meaning": "no thank you / that is fine"},
    "問診票（もんしんひょう）": {"lvl": "N2", "meaning": "medical questionnaire"},
    "保険証（ほけんしょう）": {"lvl": "N2", "meaning": "health insurance card"},
    "お薬手帳（おくすりてちょう）": {"lvl": "N2", "meaning": "medication notebook"},
    "賞味期限（しょうみきげん）": {"lvl": "N3", "meaning": "best-before date"},
    "消費期限（しょうひきげん）": {"lvl": "N3", "meaning": "expiration date"},
    "見切り品（みきりひん）": {"lvl": "N2", "meaning": "discounted goods"},
    "謙譲語（けんじょうご）": {"lvl": "N1", "meaning": "humble language"},
    "転入届（てんにゅうとどけ）": {"lvl": "N3", "meaning": "moving-in notification"},
    "住民票（じゅうみんひょう）": {"lvl": "N2", "meaning": "certificate of residence"}
}

# Update VOCAB_MASTER items with official data
updated_count = 0
for slug, items in VOCAB_MASTER.items():
    for it in items:
        raw_word = it["word"]
        pure = re.sub(r'（.*?）', '', raw_word).strip()
        reading = ""
        rm = re.search(r'（(.*?)）', raw_word)
        if rm: reading = rm.group(1).strip()
        
        target_lvl = None
        target_meaning = None
        
        # 1. Check manual official map first
        if raw_word in OFFICIAL_MANUAL_MAP:
            target_lvl = OFFICIAL_MANUAL_MAP[raw_word]["lvl"]
            target_meaning = OFFICIAL_MANUAL_MAP[raw_word]["meaning"]
        # 2. Check OpenJLPT DB
        elif pure in jlpt_db:
            target_lvl = jlpt_db[pure].get("level")
        elif reading in jlpt_db:
            target_lvl = jlpt_db[reading].get("level")
        elif pure.rstrip("する") in jlpt_db:
            target_lvl = jlpt_db[pure.rstrip("する")].get("level")
            
        if target_lvl:
            if it["jlpt"] != target_lvl:
                # print(f"[{slug}] {raw_word}: {it['jlpt']} -> {target_lvl}")
                it["jlpt"] = target_lvl
                updated_count += 1
        if target_meaning:
            it["meaning"] = target_meaning

print(f"Verified & updated {updated_count} words against official JLPT standards.")

# 3. Regenerate clean_master_vocab_boxes.json with updated JLPT levels
slug_to_box_html = {}
for slug, items in VOCAB_MASTER.items():
    slug_to_box_html[slug] = generate_vocab_box_html(items)

aliases = {
    "kotoba-no-aya-sonosetsu-wa-doumo": "kotoba-no-aya-sonosetsu-wa-doumo-thanks-and-apology",
    "kotoba-no-aya-the-seven-faces-of-sumimasen": "kotoba-no-aya-the-seven-faces-of-sumimasen-apology-thanks-call",
    "japanese-comparing-zenzen-and-mattaku-differences": "japanese-comparing-zenzen-and-mattaku-differences-in-degree-and-nuance"
}
for short_slug, full_slug in aliases.items():
    if full_slug in slug_to_box_html:
        slug_to_box_html[short_slug] = slug_to_box_html[full_slug]

with open('clean_master_vocab_boxes.json', 'w', encoding='utf-8') as f:
    json.dump(slug_to_box_html, f, ensure_ascii=False, indent=2)

print("Saved updated clean_master_vocab_boxes.json.")

# 4. Update Markdown files
import glob
updated_md = 0
for md in glob.glob('content/posts/*.md'):
    fname = os.path.basename(md)
    slug = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', fname).replace('.md', '')
    if slug in VOCAB_MASTER:
        items = VOCAB_MASTER[slug]
        new_md_sec = generate_vocab_markdown(items)
        with open(md, 'r', encoding='utf-8') as f:
            content = f.read()
        pat = r'##\s*🎯?\s*.*?(?:語彙|ボキャブラリー).*?\n.*?(?=\n---|\Z)'
        if re.search(pat, content, re.DOTALL):
            new_content = re.sub(pat, new_md_sec.strip(), content, flags=re.DOTALL)
            if new_content != content:
                with open(md, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                updated_md += 1

print(f"Updated {updated_md} Markdown files with official JLPT levels.")
