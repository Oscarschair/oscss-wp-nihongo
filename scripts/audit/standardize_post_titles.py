import glob
import os
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

files = sorted(glob.glob('content/posts/*.md'))

# ルール定義
CATEGORY_MAP = {
    'street': ('街角サバイバル', '街角サバイバル：'),
    'kotoba': ('ことばのあや', 'ことばのあや：'),
    'culture': ('カルチャーショック', 'カルチャーショック：'),
    'comparing': ('くらべてみました', 'くらべてみました：')
}

def determine_type(slug, cat_str, title_str):
    s = slug.lower()
    c = cat_str.lower()
    t = title_str.lower()
    
    # スラッグを最優先で判定
    if s.startswith('culture-shock'):
        return 'culture'
    if s.startswith('street-japanese') or s.startswith('street-'):
        return 'street'
    if s.startswith('kotoba-no-aya'):
        return 'kotoba'
    if s.startswith('japanese-comparing') or 'comparing' in s:
        return 'comparing'
        
    if 'カルチャー' in c or 'ショック' in c:
        return 'culture'
    if 'street' in s or '街角' in c or 'サバイバル' in c:
        return 'street'
    if 'kotoba' in s or 'あや' in c:
        return 'kotoba'
    if 'comparing' in s or 'くらべて' in c or '納得' in c:
        return 'comparing'
    return None

updated_count = 0

for f in files:
    if os.path.getsize(f) == 0:
        continue
    with open(f, 'r', encoding='utf-8') as fp:
        content = fp.read()
    
    parts = re.split(r'^---\s*$', content, maxsplit=2, flags=re.MULTILINE)
    if len(parts) < 3:
        continue
        
    fm = parts[1]
    body = parts[2]
    
    slug_m = re.search(r'slug:\s*["\']?([^"\']+)["\']?', fm)
    cat_m = re.search(r'categories:\s*\n\s*-\s*["\']?([^"\']+)["\']?', fm)
    title_m = re.search(r'title:\s*["\'](.*?)["\']\s*$', fm, flags=re.MULTILINE)
    
    slug = slug_m.group(1).strip() if slug_m else ""
    cat = cat_m.group(1).strip() if cat_m else ""
    title = title_m.group(1).strip() if title_m else ""
    
    ptype = determine_type(slug, cat, title)
    if not ptype:
        print(f"Unknown type: {slug} | cat={cat} | title={title[:30]}")
        continue
        
    target_cat_name, target_prefix = CATEGORY_MAP[ptype]
    
    # 1. カテゴリー名の統一 (例: 'くらべて納得！' -> 'くらべてみました')
    new_fm = fm
    cat_block_m = re.search(r'(categories:\s*\n)((?:\s*-\s*[^\n]+\n?)+)', new_fm)
    if cat_block_m:
        new_cat_block = f'{cat_block_m.group(1)}  - "{target_cat_name}"\n'
        new_fm = new_fm[:cat_block_m.start()] + new_cat_block + new_fm[cat_block_m.end():]
        
    # 2. タイトルのプレフィックスの統一
    # 既存のプレフィックス（ルビ付き含む）を除去
    clean_title = title
    # 既存のルビ付きまたはプレーンなプレフィックスパターン
    prefixes_to_strip = [
        r'^(?:<ruby>街角<rt>.*?</rt></ruby>|街角)サバイバル[：:]\s*',
        r'^街角サバイバル[：:]\s*',
        r'^(?:<ruby>言葉<rt>.*?</rt></ruby>|ことば)のあや[：:]\s*',
        r'^ことばのあや[：:]\s*',
        r'^カルチャーショック[：:]\s*',
        r'^くらべてみました[：:]\s*',
        r'^くらべて<ruby>納得<rt>.*?</rt></ruby>[！!]?[：:]\s*',
        r'^くらべて納得[！!]?[：:]\s*',
    ]
    for p_pat in prefixes_to_strip:
        clean_title = re.sub(p_pat, '', clean_title)
        
    # 新しい正式タイトル: target_prefix + clean_title
    final_title = f"{target_prefix}{clean_title}"
    
    # fm 内の title を置換
    new_fm = re.sub(r'^(title:\s*["\']).*?(["\']\s*)$', f'\\g<1>{final_title}\\g<2>', new_fm, flags=re.MULTILINE)
    
    if new_fm != fm:
        updated_count += 1
        with open(f, 'w', encoding='utf-8') as fp:
            fp.write(f"---{new_fm}---{body}")
        print(f"Updated: {os.path.basename(f)}")
        print(f"  -> Cat: {target_cat_name}")
        print(f"  -> Title: {re.sub(r'<[^>]+>', '', final_title)[:60]}")

print(f"\nCompleted! Total updated posts: {updated_count}")
