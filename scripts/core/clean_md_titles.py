import re
import glob

files = [
    'content/posts/2026-10-13-kotoba-no-aya-is-shouchidesu-wrong-business-japanese-trap.md',
    'content/posts/2026-10-14-street-japanese-city-hall-resident-registration-dungeon-guide.md',
    'content/posts/2026-10-15-japanese-comparing-rashii-souda-youda-differences.md'
]

for fp in files:
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()

    def clean_title(m):
        raw = m.group(1)
        cleaned = re.sub(r'<ruby>(.*?)<rt>.*?</rt></ruby>', r'\1', raw)
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        return f'title: "{cleaned}"'

    new_content = re.sub(r'^title:\s*["\']?(.*?)["\']?$', clean_title, content, flags=re.MULTILINE)
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Cleaned {fp}")
