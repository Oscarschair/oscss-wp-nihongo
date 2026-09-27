import sys
import re
import math

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 10/13, 10/14, 10/15 を Gutenbergレンダリング後で 4,200〜4,400字（約9分）に整える

def calc_rendered_len(md_content):
    # Markdown -> Gutenberg -> テキスト抽出の簡易エミュレーション
    # frontmatter除去
    body = re.split(r'^---\s*$', md_content, maxsplit=2, flags=re.MULTILINE)[2]
    # rt除去
    text = re.sub(r'<rt>.*?</rt>', '', body)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'\s+', '', text)
    return len(text), math.ceil(len(text)/500)

print("Checking current status...")
for path in [
    'content/posts/2026-10-13-kotoba-no-aya-is-shouchidesu-wrong-business-japanese-trap.md',
    'content/posts/2026-10-14-street-japanese-city-hall-resident-registration-dungeon-guide.md',
    'content/posts/2026-10-15-japanese-comparing-rashii-souda-youda-differences.md'
]:
    with open(path, 'r', encoding='utf-8') as f:
        t = f.read()
    chars, mins = calc_rendered_len(t)
    print(f"{path.split('/')[-1]}: {chars} chars -> 約{mins}分")
