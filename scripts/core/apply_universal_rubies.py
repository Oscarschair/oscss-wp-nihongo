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
        return surface  # No kanji
    
    reading_hira = jaconv.kata2hira(reading_kata)
    
    # Prefix match
    pre_len = 0
    while pre_len < len(surface) and pre_len < len(reading_hira):
        if surface[pre_len] == reading_hira[pre_len] and not re.match(r'[\u4e00-\u9faf]', surface[pre_len]):
            pre_len += 1
        else:
            break
            
    # Suffix match
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
    
    # If no kanji in remaining part or rt is empty, return original
    if not re.search(r'[\u4e00-\u9faf]', kanji_part) or not rt_part:
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
    # 1. Separate frontmatter
    parts = re.split(r'^---\s*$', content, maxsplit=2, flags=re.MULTILINE)
    if len(parts) >= 3:
        header = f"---{parts[1]}---\n"
        body = parts[2]
    else:
        header = ""
        body = content

    placeholders = []
    
    def repl(m):
        idx = len(placeholders)
        placeholders.append(m.group(0))
        return f"__PROTECTED_{idx}__"

    # Protect code blocks
    body = re.sub(r'```[\s\S]*?```', repl, body)
    
    # Protect inline code
    body = re.sub(r'`[^`]+`', repl, body)
    
    # Protect markdown images ![alt](url)
    body = re.sub(r'!\[.*?\]\(.*?\)', repl, body)
    
    # Protect existing ruby tags <ruby>...</ruby>
    body = re.sub(r'<ruby>[\s\S]*?</ruby>', repl, body)
    
    # Protect markdown link URLs [text](url) -> protect url
    def link_url_repl(m):
        txt = m.group(1)
        url = m.group(2)
        idx = len(placeholders)
        placeholders.append(url)
        return f"[{txt}](__PROTECTED_{idx}__)"
    body = re.sub(r'\[(.*?)\]\((.*?)\)', link_url_repl, body)
    
    # Protect HTML tags
    body = re.sub(r'<[^>]+>', repl, body)

    # Now split body by protected placeholders and lines
    segments = re.split(r'(__PROTECTED_\d+__)', body)
    processed_segments = []
    
    for seg in segments:
        if re.match(r'^__PROTECTED_\d+__$', seg):
            processed_segments.append(seg)
        else:
            # Segment contains normal text, headers, table pipes, lists, etc.
            # Process lines
            lines = seg.split('\n')
            p_lines = []
            for line in lines:
                # If table header or separator line (e.g. | :--- |)
                if re.match(r'^\s*\|?\s*[-:]+[-| :]*$', line):
                    p_lines.append(line)
                    continue
                if re.search(r'[\u4e00-\u9faf]', line):
                    p_lines.append(process_text_segment(line))
                else:
                    p_lines.append(line)
            processed_segments.append('\n'.join(p_lines))

    new_body = "".join(processed_segments)

    # Restore placeholders
    for idx, orig in enumerate(placeholders):
        new_body = new_body.replace(f"__PROTECTED_{idx}__", orig)

    return header + new_body

if __name__ == '__main__':
    posts = sorted(glob.glob('content/posts/*.md'))
    print(f"Applying universal rubies to {len(posts)} posts...")
    
    total_rubies = 0
    for p in posts:
        with open(p, 'r', encoding='utf-8') as f:
            c = f.read()
        
        before_count = len(re.findall(r'<ruby>', c))
        new_c = apply_ruby_to_markdown(c)
        after_count = len(re.findall(r'<ruby>', new_c))
        
        with open(p, 'w', encoding='utf-8') as f:
            f.write(new_c)
            
        added = after_count - before_count
        total_rubies += after_count
        print(f"{os.path.basename(p):65} | rubies: {before_count} -> {after_count} (+{added})")
        
    print(f"Done! Total rubies in all posts: {total_rubies}")
