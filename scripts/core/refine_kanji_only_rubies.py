import glob, re, os, sys
sys.stdout.reconfigure(encoding='utf-8')

# ひらがな・カタカナを含まない純粋な「漢字のみルビ」変換辞書
# 漢字のみにルビを振り、送り仮名や接頭辞（ひらがな・カタカナ）はルビの外に出す
KANJI_ONLY_REPLACEMENTS = {
    # 太る・太っている
    "<ruby>太る<rt>ふとる</rt></ruby>": "<ruby>太<rt>ふと</rt></ruby>る",
    "<ruby>太っている<rt>ふとっている</rt></ruby>": "<ruby>太<rt>ふと</rt></ruby>っている",

    # 替え玉
    "<ruby>替え玉<rt>かえだま</rt></ruby>": "<ruby>替<rt>か</rt></ruby>え<ruby>玉<rt>だま</rt></ruby>",

    # お冷・湯呑み
    "<ruby>お冷<rt>おひや</rt></ruby>": "お<ruby>冷<rt>ひや</rt></ruby>",
    "<ruby>湯呑み<rt>ゆのみ</rt></ruby>": "<ruby>湯呑<rt>ゆの</rt></ruby>み",

    # 台拭き・紙エプロン
    "<ruby>台拭き<rt>ふきん</rt></ruby>": "<ruby>台拭<rt>だいふ</rt></ruby>き",
    "<ruby>紙エプロン<rt>かみえぷろん</rt></ruby>": "<ruby>紙<rt>かみ</rt></ruby>エプロン",

    # かけ湯・さび抜き
    "<ruby>かけ湯<rt>かけゆ</rt></ruby>": "かけ<ruby>湯<rt>ゆ</rt></ruby>",
    "<ruby>さび抜き<rt>さびぬき</rt></ruby>": "さび<ruby>抜<rt>ぬ</rt></ruby>き",

    # お会計・お通し・お天道様
    "<ruby>お会計<rt>おかいけい</rt></ruby>": "お<ruby>会計<rt>かいけい</rt></ruby>",
    "<ruby>お通し<rt>おとおし</rt></ruby>": "お<ruby>通<rt>とお</rt></ruby>し",
    "<ruby>お天道様<rt>おてんとさま</rt></ruby>": "お<ruby>天道様<rt>てんとさま</rt></ruby>",

    # 少し・持ち帰り・全く・済む
    "<ruby>少し<rt>すこし</rt></ruby>": "<ruby>少<rt>すこ</rt></ruby>し",
    "<ruby>持ち帰り<rt>もちかえり</rt></ruby>": "<ruby>持<rt>も</rt></ruby>ち<ruby>帰<rt>かえ</rt></ruby>り",
    "<ruby>全く<rt>まったく</rt></ruby>": "<ruby>全<rt>まった</rt></ruby>く",
    "<ruby>済む<rt>すむ</rt></ruby>": "<ruby>済<rt>す</rt></ruby>む",
}

files = sorted(glob.glob('content/posts/*.md'))
total_updated = 0

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as fp:
        content = fp.read()
    
    original = content
    for old_ruby, new_ruby in KANJI_ONLY_REPLACEMENTS.items():
        content = content.replace(old_ruby, new_ruby)
        
    if content != original:
        with open(fpath, 'w', encoding='utf-8') as fp:
            fp.write(content)
        total_updated += 1
        print(f"Updated kanji-only ruby in: {os.path.basename(fpath)}")

print(f"\nCompleted! Total files updated: {total_updated}")
