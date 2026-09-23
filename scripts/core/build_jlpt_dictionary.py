import csv
import json
import os
import re

levels = ['n5', 'n4', 'n3', 'n2', 'n1']

# 単語 -> {level, reading, meaning}
word_dict = {}
# レベル別単語リスト
level_words = {lvl.upper(): [] for lvl in levels}

for lvl in levels:
    lvl_upper = lvl.upper()
    csv_path = f'data/jlpt/{lvl}.csv'
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            expr = row.get('expression', '').strip()
            reading = row.get('reading', '').strip()
            meaning = row.get('meaning', '').strip()
            
            entry = {
                'level': lvl_upper,
                'expression': expr,
                'reading': reading,
                'meaning': meaning
            }
            
            level_words[lvl_upper].append(entry)
            
            # 表記で登録
            if expr:
                if expr not in word_dict:
                    word_dict[expr] = entry
                elif lvl_upper < word_dict[expr]['level']: # より高い/低い難易度の優先度
                    # N5が最も基礎、N1が最難関。基礎レベルを優先するか難度を優先するか
                    pass
            # 読みで登録（ひらがな検索用、1文字ひらがなは除外）
            if reading and len(reading) > 1 and reading != expr:
                if reading not in word_dict:
                    word_dict[reading] = entry

summary = {
    'total_unique_keys': len(word_dict),
    'counts_by_level': {lvl: len(words) for lvl, words in level_words.items()}
}

output_data = {
    'summary': summary,
    'dictionary': word_dict,
    'by_level': level_words
}

out_path = 'data/jlpt/jlpt_dictionary.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"Generated {out_path} successfully.")
print(f"Total unique keys: {len(word_dict)}")
for lvl, cnt in summary['counts_by_level'].items():
    print(f"  {lvl}: {cnt} words")
