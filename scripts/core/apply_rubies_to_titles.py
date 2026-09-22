import glob
import os
import re
import sys
import jaconv
from janome.tokenizer import Tokenizer

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

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

def apply_ruby_to_title(title_text):
    # If already has ruby, return as is
    if '<ruby>' in title_text:
        return title_text

    # Certain words correction if needed (e.g. 香港 -> ほんこん)
    return process_text_segment(title_text)

def main():
    posts_dir = "content/posts"
    files = sorted(glob.glob(os.path.join(posts_dir, "*.md")))
    updated_count = 0

    for fpath in files:
        if os.path.getsize(fpath) == 0:
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        parts = re.split(r"^---\s*$", content, maxsplit=2, flags=re.MULTILINE)
        if len(parts) < 3:
            continue

        fm = parts[1]
        body = parts[2]

        title_match = re.search(r'^(title:\s*["\'])(.*?)(["\']\s*)$', fm, flags=re.MULTILINE)
        if not title_match:
            title_match = re.search(r'^(title:\s*)([^\r\n]+)$', fm, flags=re.MULTILINE)
            if not title_match:
                continue
            orig_title = title_match.group(2).strip()
            quote_pre = 'title: "'
            quote_post = '"'
        else:
            orig_title = title_match.group(2)
            quote_pre = 'title: "'
            quote_post = '"'

        if '<ruby>' in orig_title:
            print(f"Skipping already rubied title: {os.path.basename(fpath)}")
            continue

        new_title = apply_ruby_to_title(orig_title)
        if new_title != orig_title:
            # Replace title line in frontmatter
            if title_match.group(0).endswith('\n'):
                target_str = title_match.group(0).rstrip('\r\n')
            else:
                target_str = title_match.group(0)

            new_line = f'{quote_pre}{new_title}{quote_post}'
            new_fm = fm.replace(target_str, new_line, 1)

            new_content = f"---{new_fm}---{body}"
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)

            print(f"Updated: {os.path.basename(fpath)}")
            print(f"  Old: {orig_title}")
            print(f"  New: {new_title}\n")
            updated_count += 1

    print(f"Total titles updated with rubies: {updated_count}/{len(files)}")

if __name__ == "__main__":
    main()
