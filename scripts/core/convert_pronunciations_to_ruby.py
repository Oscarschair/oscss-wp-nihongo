import glob, re, os, sys
sys.stdout.reconfigure(encoding='utf-8')

# 正確なふりがな・発音ペア辞書（全記事の文脈精査済み）
# key: 置換前テキスト, val: 置換後HTML
REPLACEMENTS = {
    # ラーメン記事
    "替え玉（かえだま）": "<ruby>替え玉<rt>かえだま</rt></ruby>",
    "替え玉 (かえだま)": "<ruby>替え玉<rt>かえだま</rt></ruby>",
    "丼（どんぶり）": "<ruby>丼<rt>どんぶり</rt></ruby>",
    "台拭き（ふきん）": "<ruby>台拭き<rt>ふきん</rt></ruby>",
    "暖簾（のれん）": "<ruby>暖簾<rt>のれん</rt></ruby>",
    "普通（ふつう）": "<ruby>普通<rt>ふつう</rt></ruby>",
    "替玉（かえだま）": "<ruby>替玉<rt>かえだま</rt></ruby>",
    "紙エプロン（かみえぷろん）": "<ruby>紙エプロン<rt>かみえぷろん</rt></ruby>",

    # 回転寿司記事
    "お冷（おひや）": "<ruby>お冷<rt>おひや</rt></ruby>",
    "お冷 (おひや)": "<ruby>お冷<rt>おひや</rt></ruby>",
    "湯呑み（ゆのみ）": "<ruby>湯呑み<rt>ゆのみ</rt></ruby>",

    # 太るvs太っている
    "太る（ふとる）": "<ruby>太る<rt>ふとる</rt></ruby>",
    "太っている（ふとっている）": "<ruby>太っている<rt>ふとっている</rt></ruby>",
    "恰幅（かっぷく）": "<ruby>恰幅<rt>かっぷく</rt></ruby>",

    # カフェでスマホ放置
    "お天道様（おてんとさま）": "<ruby>お天道様<rt>おてんとさま</rt></ruby>",

    # 傘立て
    "傘の袋（かさのふくろ）": "<ruby>傘<rt>かさ</rt></ruby>の<ruby>袋<rt>ふくろ</rt></ruby>",
    "鍵（かぎ）": "<ruby>鍵<rt>かぎ</rt></ruby>",

    # 音姫・トイレ
    "音姫（おとひめ）": "<ruby>音姫<rt>おとひめ</rt></ruby>",
    "雅（みやび）": "<ruby>雅<rt>みやび</rt></ruby>",

    # 適当
    "適切に（てきせつに）": "<ruby>適切<rt>てきせつ</rt></ruby>に",
    "妥当な（だとうな）": "<ruby>妥当<rt>だとう</rt></ruby>な",

    # 温泉・銭湯
    "かけ湯（かけゆ）": "<ruby>かけ湯<rt>かけゆ</rt></ruby>",
    "畳（たたみ）": "<ruby>畳<rt>たたみ</rt></ruby>",

    # ちょっとvs少し
    "少し（すこし）": "<ruby>少し<rt>すこし</rt></ruby>",
    "ちょっと（一寸）": "<ruby>一寸<rt>ちょっと</rt></ruby>",

    # カフェ注文
    "店内（てんない）": "<ruby>店内<rt>てんない</rt></ruby>",
    "店内で（てんないで）": "<ruby>店内<rt>てんない</rt></ruby>で",
    "持ち帰りで（もちかえりで）": "<ruby>持ち帰り<rt>もちかえり</rt></ruby>で",
    "軽減税率（けいげんぜいりつ）": "<ruby>軽減税率<rt>けいげんぜいりつ</rt></ruby>",
    "紙袋（かみぶくろ）": "<ruby>紙袋<rt>かみぶくろ</rt></ruby>",
    "小分けの紙袋（かみぶくろ）": "小分けの<ruby>紙袋<rt>かみぶくろ</rt></ruby>",
    "袋（ふくろ）": "<ruby>袋<rt>ふくろ</rt></ruby>",

    # その節はどうも
    "節（せつ）": "<ruby>節<rt>せつ</rt></ruby>",

    # すみません
    "謝罪（あやまる）": "<ruby>謝罪<rt>しゃざい</rt></ruby>",
    "会釈（どうも）": "<ruby>会釈<rt>えしゃく</rt></ruby>",
    "済む（すむ）": "<ruby>済む<rt>すむ</rt></ruby>",

    # 全然vs全く
    "全然（ぜんぜん）": "<ruby>全然<rt>ぜんぜん</rt></ruby>",
    "全く（まったく）": "<ruby>全く<rt>まったく</rt></ruby>",

    # 居酒屋
    "お通し（おとおし）": "<ruby>お通し<rt>おとおし</rt></ruby>",
    "お会計（かいけい）": "<ruby>お会計<rt>おかいけい</rt></ruby>",
    "別々（べつべつ）": "<ruby>別々<rt>べつべつ</rt></ruby>",
    "一緒（いっしょ）": "<ruby>一緒<rt>いっしょ</rt></ruby>",

    # 美容室
    "梳（す）": "<ruby>梳<rt>す</rt></ruby>",
    "襟足（えりあし）": "<ruby>襟足<rt>えりあし</rt></ruby>",

    # 大丈夫
    "大丈夫（だいじょうぶ）": "<ruby>大丈夫<rt>だいじょうぶ</rt></ruby>",

    # 役割語
    "役割語（やくわりご）": "<ruby>役割語<rt>やくわりご</rt></ruby>",
}

# さらに、一般的なパターン（漢字熟語＋カッコ内ひらがな）を自動検知して置換する
# [一-龥々ヶ]+[（\(][ぁ-んー]+[）\)]
kanji_strict_pat = re.compile(r'([一-龥々ヶ]{1,6})[（\(]([ぁ-んー]{1,12})[）\)]')

files = sorted(glob.glob('content/posts/*.md'))
total_replacements = 0

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as fp:
        content = fp.read()
    
    parts = re.split(r'^---\s*$', content, maxsplit=2, flags=re.MULTILINE)
    if len(parts) < 3:
        continue
    
    header = parts[1]
    body = parts[2]
    
    original_body = body
    
    # 1. 辞書マッチング（確実なもの）
    for k, v in REPLACEMENTS.items():
        body = body.replace(k, v)
        
    # 2. 厳密な漢字のみ＋ひらがなふりがなの自動変換
    def auto_ruby_repl(m):
        kanji = m.group(1)
        ruby = m.group(2)
        # 除外キーワード
        if ruby in ['例', 'まとめ', '補足', '注意', '税込', '税抜', '笑', 'どうぞ', 'あやまる', 'どうも']:
            return m.group(0)
        return f"<ruby>{kanji}<rt>{ruby}</rt></ruby>"
    
    body = kanji_strict_pat.sub(auto_ruby_repl, body)
    
    if body != original_body:
        new_content = f"---{header}---{body}"
        with open(fpath, 'w', encoding='utf-8') as fp:
            fp.write(new_content)
        total_replacements += 1
        print(f"Updated ruby in: {os.path.basename(fpath)}")

print(f"\nCompleted! Total files updated: {total_replacements}")
