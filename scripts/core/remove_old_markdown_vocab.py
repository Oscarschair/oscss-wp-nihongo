# -*- coding: utf-8 -*-
import glob
import os
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

files = sorted(glob.glob('content/posts/*.md'))
cleaned_count = 0

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
    
    new_lines = []
    i = 0
    in_old_vocab = False
    removed_in_file = False
    
    while i < len(lines):
        line = lines[i]
        
        # もし c-vocab-box の開始行なら、古い語彙セクションではないので通常処理
        if '<div class="c-vocab-box"' in line:
            in_old_vocab = False
            new_lines.append(line)
            i += 1
            continue
        
        # 行のプレーンテキスト化（ルビ・HTMLタグ除去）
        plain_line = re.sub(r'<rt>.*?</rt>', '', line)
        plain_line = re.sub(r'<[^>]+>', '', plain_line).strip()
        
        # 古い語彙セクションの見出し検知（## 今回の語彙 など）
        if (plain_line.startswith('##') or plain_line.startswith('###')) and \
           ('今回の語彙' in plain_line or '重要ボキャブラリー' in plain_line):
            in_old_vocab = True
            removed_in_file = True
            i += 1
            continue
        
        if in_old_vocab:
            # 終了判定: 次の大見出し(## )、仕切り線(---)、ショートコード([oscss_)、または c-vocab-box
            if plain_line.startswith('## ') or plain_line == '---' or plain_line.startswith('[oscss_') or '<div class="c-vocab-box"' in line:
                in_old_vocab = False
                new_lines.append(line)
                i += 1
                continue
            else:
                # 古い語彙セクションの中（スキップ）
                i += 1
                continue
        
        new_lines.append(line)
        i += 1
    
    if removed_in_file:
        cleaned_text = "".join(new_lines)
        # 余分な連続空行を整理
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text).strip() + '\n'
        with open(f, 'w', encoding='utf-8') as fp:
            fp.write(cleaned_text)
        cleaned_count += 1
        print(f"[CLEANED] {os.path.basename(f)}")

print(f"\nTotal files cleaned: {cleaned_count} / {len(files)}")
