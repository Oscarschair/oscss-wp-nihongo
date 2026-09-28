import glob
import os
import re
import sys
import jaconv
from janome.tokenizer import Tokenizer

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

tokenizer = Tokenizer()

# Custom word overrides for accurate Japanese learning pronunciation
CUSTOM_READING_OVERRIDES = {
    "香港": [("香港", "ほんこん")],
    "日本": [("日本", "にほん")],
    "日本語": [("日本", "にほん"), ("語", "ご")],
    "美容室": [("美容", "びよう"), ("室", "しつ")],
    "居酒屋": [("居酒屋", "いざかや")],
    "自販機": [("自販機", "じはんき")],
    "シャンプー台": [("台", "だい")],
    "お冷": [("冷", "ひや")],
    "お湯": [("湯", "ゆ")],
    "お会計": [("会計", "かいけい")],
    "お通し": [("通", "とお")],
    "お天道様": [("天道様", "てんとさま")],
    "替え玉": [("替", "か"), ("玉", "だま")],
    "台拭き": [("台拭", "だいふ")],
    "紙エプロン": [("紙", "かみ")],
    "さび抜き": [("抜", "ぬ")],
    "湯呑み": [("湯呑", "ゆの")],
    "太る": [("太", "ふと")],
    "太っている": [("太", "ふと")],
    "少し": [("少", "すこ")],
    "持ち帰り": [("持", "も"), ("帰", "かえ")],
    "全く": [("全", "まった")],
    "済む": [("済", "す")],
    "承知": [("承知", "しょうち")],
    "了解": [("了解", "りょうかい")],
}

KANJI_CHAR = r'[\u4e00-\u9faf々〆ヵヶ]'
HIRA_CHAR = r'[ぁ-んー]'

def align_ruby(surface, reading_kata):
    if not re.search(KANJI_CHAR, surface):
        return surface  # No kanji

    reading_hira = jaconv.kata2hira(reading_kata)

    # Prefix match (strip leading hiragana/katakana that match reading)
    pre_len = 0
    while pre_len < len(surface) and pre_len < len(reading_hira):
        if surface[pre_len] == reading_hira[pre_len] and not re.match(KANJI_CHAR, surface[pre_len]):
            pre_len += 1
        else:
            break

    # Suffix match (strip trailing hiragana/katakana that match reading)
    suf_len = 0
    while suf_len < (len(surface) - pre_len) and suf_len < (len(reading_hira) - pre_len):
        if surface[-1 - suf_len] == reading_hira[-1 - suf_len] and not re.match(KANJI_CHAR, surface[-1 - suf_len]):
            suf_len += 1
        else:
            break

    prefix = surface[:pre_len]
    suffix = surface[len(surface) - suf_len:] if suf_len > 0 else ''
    kanji_part = surface[pre_len:len(surface) - suf_len if suf_len > 0 else len(surface)]
    rt_part = reading_hira[pre_len:len(reading_hira) - suf_len if suf_len > 0 else len(reading_hira)]

    # If no kanji in remaining part or rt is empty or identical to kanji
    if not re.search(KANJI_CHAR, kanji_part) or not rt_part or kanji_part == rt_part:
        return surface

    return f'{prefix}<ruby>{kanji_part}<rt>{rt_part}</rt></ruby>{suffix}'

def process_text_segment(text):
    tokens = tokenizer.tokenize(text)
    out = []
    for tok in tokens:
        surface = tok.surface
        if surface in CUSTOM_READING_OVERRIDES:
            token_res = surface
            for k_part, rt_part in CUSTOM_READING_OVERRIDES[surface]:
                token_res = token_res.replace(k_part, f'<ruby>{k_part}<rt>{rt_part}</rt></ruby>')
            out.append(token_res)
        elif re.search(KANJI_CHAR, surface):
            out.append(align_ruby(surface, tok.reading))
        else:
            out.append(surface)
    return "".join(out)

def apply_ruby_to_content(content):
    # Separate frontmatter
    parts = re.split(r'^---\s*$', content, maxsplit=2, flags=re.MULTILINE)
    if len(parts) >= 3:
        frontmatter = parts[1]
        body = parts[2]
    else:
        frontmatter = ""
        body = content

    # 1. Update frontmatter title if not yet rubied
    title_match = re.search(r'^(title:\s*["\']?)(.*?)(["\']?\s*)$', frontmatter, flags=re.MULTILINE)
    if title_match and '<ruby>' not in title_match.group(2):
        orig_t = title_match.group(2)
        # Preserve 【4コマ漫画】or emojis without extra spaces
        new_t = process_text_segment(orig_t)
        frontmatter = frontmatter.replace(title_match.group(0), f'title: "{new_t}"\n')

    # 2. Process body with rich protection
    placeholders = []
    def repl(m):
        idx = len(placeholders)
        placeholders.append(m.group(0))
        return f"__PROTECTED_{idx}__"

    # Protect code blocks
    body = re.sub(r'```[\s\S]*?```', repl, body)

    # Protect inline code
    body = re.sub(r'`[^`\n]+`', repl, body)

    # Protect markdown images
    body = re.sub(r'!\[.*?\]\(.*?\)', repl, body)

    # Protect shortcodes: [oscss_...]
    body = re.sub(r'\[oscss_[^\]]+\]', repl, body)

    # Protect existing ruby tags
    body = re.sub(r'<ruby[\s\S]*?</ruby>', repl, body)

    # Protect Cantonese quote lines: > 🇭🇰 ...
    def cantonese_quote_repl(m):
        idx = len(placeholders)
        placeholders.append(m.group(0))
        return f"__PROTECTED_{idx}__"
    body = re.sub(r'^>\s*🇭🇰.*$', cantonese_quote_repl, body, flags=re.MULTILINE)

    # Protect markdown link URLs [text](url) -> protect only url
    def link_url_repl(m):
        txt = m.group(1)
        url = m.group(2)
        idx = len(placeholders)
        placeholders.append(url)
        return f"[{txt}](__PROTECTED_{idx}__)"
    body = re.sub(r'\[(.*?)\]\((.*?)\)', link_url_repl, body)

    # Protect HTML tags
    body = re.sub(r'<[^>]+>', repl, body)

    # Protect vocab box header items: * **漢字（ひらがな）** 【JLPT ...】
    def vocab_header_repl(m):
        idx = len(placeholders)
        placeholders.append(m.group(0))
        return f"__PROTECTED_{idx}__"
    body = re.sub(r'^\*\s*\*\*[^*]+?\([ぁ-んー]+\)\*\*\s*【(?:JLPT\s*)?[Nn][1-5]】.*$', vocab_header_repl, body, flags=re.MULTILINE)

    # Split body by placeholders
    segments = re.split(r'(__PROTECTED_\d+__)', body)
    processed_segments = []

    # To track table columns
    table_cantonese_cols = set()

    for seg in segments:
        if re.match(r'^__PROTECTED_\d+__$', seg):
            processed_segments.append(seg)
        else:
            lines = seg.split('\n')
            p_lines = []
            for line in lines:
                # Table separator / header line
                if re.match(r'^\s*\|?\s*[-:]+[-| :]*$', line):
                    p_lines.append(line)
                    continue

                if line.strip().startswith('|') and line.strip().endswith('|'):
                    cells = line.split('|')
                    # Check if this is a header row
                    is_header = any(h in line for h in ['広東語', '繁体字', '中国語', '香港'])
                    if is_header:
                        table_cantonese_cols = set()
                        for c_idx, cell in enumerate(cells):
                            if any(k in cell for k in ['広東語', '繁体字', '中国語']):
                                table_cantonese_cols.add(c_idx)

                    new_cells = []
                    for c_idx, cell in enumerate(cells):
                        # Skip if Cantonese column or contains Jyutping like (tau1 ...)
                        if c_idx in table_cantonese_cols or re.search(r'\([a-z]+[1-6]', cell):
                            new_cells.append(cell)
                        elif re.search(KANJI_CHAR, cell):
                            new_cells.append(process_text_segment(cell))
                        else:
                            new_cells.append(cell)
                    p_lines.append('|'.join(new_cells))
                    continue

                # Reset table cols outside table
                if not line.strip().startswith('|'):
                    table_cantonese_cols = set()

                if re.search(KANJI_CHAR, line):
                    p_lines.append(process_text_segment(line))
                else:
                    p_lines.append(line)
            processed_segments.append('\n'.join(p_lines))

    new_body = "".join(processed_segments)

    # Restore placeholders
    for idx, orig in enumerate(placeholders):
        new_body = new_body.replace(f"__PROTECTED_{idx}__", orig)

    if frontmatter:
        return f"---{frontmatter}---{new_body}"
    return new_body

def main():
    post_files = sorted(glob.glob('content/posts/*.md'))
    manga_files = sorted(glob.glob('content/manga/*.md'))
    all_files = post_files + manga_files

    print(f"Starting Universal Ruby Batch on {len(all_files)} files...")
    
    total_added = 0
    updated_files = 0

    for fpath in all_files:
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        before_count = len(re.findall(r'<ruby>', content))
        new_content = apply_ruby_to_content(content)
        after_count = len(re.findall(r'<ruby>', new_content))
        added = after_count - before_count

        if added > 0:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            updated_files += 1
            total_added += added
            print(f"[UPDATED] {os.path.basename(fpath):<60} | {before_count} -> {after_count} (+{added})")
        else:
            print(f"[UNCHANGED] {os.path.basename(fpath):<58} | {after_count} rubies")

    print("\n" + "="*80)
    print(f"BATCH COMPLETE!")
    print(f"Total files updated: {updated_files}/{len(all_files)}")
    print(f"Total new rubies added: {total_added}")

if __name__ == '__main__':
    main()
