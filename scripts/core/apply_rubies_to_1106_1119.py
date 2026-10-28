import glob
import os
import re
import sys
import jaconv
from janome.tokenizer import Tokenizer

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

tokenizer = Tokenizer()

def align_ruby(surface, reading_kata):
    if not re.search(r'[\u4e00-\u9faf]', surface):
        return surface
    
    reading_hira = jaconv.kata2hira(reading_kata)
    
    pre_len = 0
    while pre_len < len(surface) and pre_len < len(reading_hira):
        if surface[pre_len] == reading_hira[pre_len] and not re.match(r'[\u4e00-\u9faf]', surface[pre_len]):
            pre_len += 1
        else:
            break
            
    suf_len = 0
    while suf_len < (len(surface) - pre_len) and suf_len < (len(reading_hira) - pre_len):
        if surface[-1 - suf_len] == reading_hira[-1 - suf_len] and not re.match(r'[\u4e00-\u9faf]', surface[-1 - suf_len]):
            suf_len += 1
        else:
            break
            
    prefix = surface[:pre_len]
    suffix = surface[len(surface) - suf_len:] if suf_len > 0 else ''
    kanji_part = surface[pre_len:len(surface) - suf_len if suf_len > 0 else len(surface)]
    rt_part = reading_hira[pre_len:len(reading_hira) - suf_len if suf_len > 0 else len(reading_hira)]
    
    if not re.search(r'[\u4e00-\u9faf]', kanji_part) or not rt_part or rt_part == '*':
        return surface

    if kanji_part == '笑' and rt_part == 'えみ':
        rt_part = 'わら'

    return f'{prefix}<ruby>{kanji_part}<rt>{rt_part}</rt></ruby>{suffix}'

def process_text_segment(text):
    tokens = tokenizer.tokenize(text)
    out = []
    for tok in tokens:
        if re.search(r'[\u4e00-\u9faf]', tok.surface):
            out.append(align_ruby(tok.surface, tok.reading))
        else:
            out.append(tok.surface)
    return "".join(out)

def apply_ruby_to_markdown(content):
    parts = re.split(r'^---\s*$', content, maxsplit=2, flags=re.MULTILINE)
    if len(parts) >= 3:
        fm = parts[1]
        body = parts[2]
    else:
        fm = ""
        body = content

    # ADR 0003: DO NOT apply ruby to frontmatter title or description!
    header = f"---{fm}---\n" if fm else ""

    placeholders = []
    
    def repl(m):
        idx = len(placeholders)
        placeholders.append(m.group(0))
        return f"__PROTECTED_{idx}__"

    # Protect code blocks
    body = re.sub(r'```[\s\S]*?```', repl, body)
    # Protect inline code
    body = re.sub(r'`[^`\n]+`', repl, body)
    # Protect already existing rubies
    body = re.sub(r'<ruby>[\s\S]*?<\/ruby>', repl, body)
    # Protect HTML tags (including details, summary, strong, div, span, etc)
    body = re.sub(r'<[^>]+>', repl, body)
    # Protect markdown links and image tags
    body = re.sub(r'!?\[.*?\]\(.*?\)', repl, body)
    # Protect shortcodes
    body = re.sub(r'\[oscss_.*?\]', repl, body)

    segments = re.split(r'(__PROTECTED_\d+__)', body)
    processed_segments = []
    
    for seg in segments:
        if re.match(r'^__PROTECTED_\d+__$', seg):
            processed_segments.append(seg)
        else:
            lines = seg.split('\n')
            p_lines = []
            for line in lines:
                # Skip markdown table borders
                if re.match(r'^\s*\|?\s*[-:]+[-| :]*$', line):
                    p_lines.append(line)
                    continue
                if re.search(r'[\u4e00-\u9faf]', line):
                    p_lines.append(process_text_segment(line))
                else:
                    p_lines.append(line)
            processed_segments.append('\n'.join(p_lines))

    new_body = "".join(processed_segments)

    for idx, orig in enumerate(placeholders):
        new_body = new_body.replace(f"__PROTECTED_{idx}__", orig)

    return header + new_body

posts_dir = "content/posts"
target_dates = [f"2026-11-{d:02d}" for d in range(6, 20)]
files = sorted([f for f in os.listdir(posts_dir) if any(f.startswith(d) for d in target_dates)])

print(f"Applying HTML5 rubies to {len(files)} posts (11/06 - 11/19)...")

for f in files:
    filepath = os.path.join(posts_dir, f)
    with open(filepath, 'r', encoding='utf-8') as fp:
        raw = fp.read()
    rubied = apply_ruby_to_markdown(raw)
    with open(filepath, 'w', encoding='utf-8') as fp:
        fp.write(rubied)
    print(f"Applied rubies: {f}")

print("\n[SUCCESS] All 14 posts now have clean HTML5 rubies!")
