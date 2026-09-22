import glob, re, os

for f in sorted(glob.glob('content/posts/*.md')):
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    parts = re.split(r'^---\s*$', c, maxsplit=2, flags=re.MULTILINE)
    body = parts[2] if len(parts) >= 3 else c
    
    # 漢字を含む単語の直後のカッコ内ひらがな（読み仮名）
    # 例: 替え玉（かえだま）、丼（どんぶり）、台拭き（ふきん）、お冷（おひや）、暖簾（のれん）
    matches = re.findall(r'([一-龥々ヶぁ-ん]*[一-龥々ヶ]+[ぁ-ん]*)[（\(]([ぁ-んー\s]+)[）\)]', body)
    valid = []
    for word, ruby in matches:
        ruby_clean = ruby.strip()
        if ruby_clean in ['例', 'まとめ', '補足', '注意', '税込', '税抜', '笑']:
            continue
        # 数字や英字がないひらがなのみ
        if re.match(r'^[ぁ-んー\s]+$', ruby_clean):
            valid.append((word, ruby_clean))
    
    if valid:
        print(f"=== {os.path.basename(f)} ({len(valid)}) ===")
        for w, r in valid:
            print(f"  {w} -> <ruby>{w}<rt>{r}</rt></ruby>")
