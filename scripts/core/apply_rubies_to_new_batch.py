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

    # Title in frontmatter: apply ruby to title text
    title_match = re.search(r'^(title:\s*["\'])(.*?)(["\']\s*)$', fm, flags=re.MULTILINE)
    if title_match:
        orig_t = title_match.group(2)
        if '<ruby>' not in orig_t:
            rubied_t = process_text_segment(orig_t)
            fm = fm.replace(title_match.group(0), f'title: "{rubied_t}"\n', 1)

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
    # Protect HTML tags
    body = re.sub(r'<[^>]+>', repl, body)
    # Protect markdown links and image tags
    body = re.sub(r'!?\[.*?\]\(.*?\)', repl, body)
    # Protect shortcodes
    body = re.sub(r'\[oscss_.*?\]', repl, body)
    # Protect Cantonese phrases (我嚟緊啦 etc)
    body = re.sub(r'我嚟緊啦！', repl, body)
    body = re.sub(r'我马上来！', repl, body)

    segments = re.split(r'(__PROTECTED_\d+__)', body)
    processed_segments = []
    
    for seg in segments:
        if re.match(r'^__PROTECTED_\d+__$', seg):
            processed_segments.append(seg)
        else:
            lines = seg.split('\n')
            p_lines = []
            for line in lines:
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

target_files = [
    "content/posts/2026-10-06-japanese-comparing-iku-vs-kuru-perspective-trap.md",
    "content/posts/2026-10-07-street-japanese-delivery-redelivery-undelivered-notice-dungeon-guide.md",
    "content/posts/2026-10-08-kotoba-no-aya-the-trap-of-kekkoudesu-yes-or-no.md",
    "content/posts/2026-10-09-culture-shock-hanko-seal-stamp-culture-and-signature.md",
    "content/posts/2026-10-10-street-japanese-clinic-medical-questionnaire-pharmacy-guide.md",
    "content/posts/2026-10-11-japanese-comparing-hazu-vs-wake-nuance-differences.md",
    "content/posts/2026-10-12-culture-shock-shoumi-kigen-vs-shouhi-kigen-discount-stickers.md",
]

for tf in target_files:
    if os.path.exists(tf):
        with open(tf, 'r', encoding='utf-8') as f:
            raw = f.read()
        rubied = apply_ruby_to_markdown(raw)
        with open(tf, 'w', encoding='utf-8') as f:
            f.write(rubied)
        print(f"Applied rubies to: {os.path.basename(tf)}")
