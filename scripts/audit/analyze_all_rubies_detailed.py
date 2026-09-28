import glob
import os
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

KANJI = r'[\u4e00-\u9faf々〆ヵヶ]'
HIRA = r'[ぁ-んー]'
KATA = r'[ァ-ヶー]'

def analyze_post(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()

    parts = re.split(r'^---\s*$', text, maxsplit=2, flags=re.MULTILINE)
    frontmatter = parts[1] if len(parts) >= 3 else ""
    body = parts[2] if len(parts) >= 3 else text

    # Extract title
    title_match = re.search(r'^title:\s*["\']?(.*?)["\']?$', frontmatter, re.MULTILINE)
    title = title_match.group(1) if title_match else ""

    # Count rubies in title vs body
    title_rubies = re.findall(r'<ruby>(.*?)<rt>(.*?)</rt></ruby>', title)
    body_rubies = re.findall(r'<ruby>(.*?)<rt>(.*?)</rt></ruby>', body)
    
    # Check true nested rubies: <ruby[^>]*>(?:(?!</ruby>).)*?<ruby[^>]*>
    nested = re.findall(r'<ruby[^>]*>(?:(?!</ruby>).)*?<ruby[^>]*>', text, re.DOTALL)

    # Check unclosed or mismatched tags
    open_ruby = len(re.findall(r'<ruby\b', text))
    close_ruby = len(re.findall(r'</ruby>', text))
    open_rt = len(re.findall(r'<rt\b', text))
    close_rt = len(re.findall(r'</rt>', text))
    
    tag_errors = []
    if open_ruby != close_ruby:
        tag_errors.append(f"ruby tags: open={open_ruby}, close={close_ruby}")
    if open_rt != close_rt:
        tag_errors.append(f"rt tags: open={open_rt}, close={close_rt}")
    if open_ruby != open_rt:
        tag_errors.append(f"tag count: ruby={open_ruby}, rt={open_rt}")

    # Inspect all rubies
    all_rubies = title_rubies + body_rubies
    
    # Categories of potential issues
    okurigana_leaks = []  # base ends with hiragana: <ruby>食べる<rt>たべる</rt></ruby>
    prefix_leaks = []     # base starts with hiragana: <ruby>お茶<rt>おちゃ</rt></ruby>
    no_kanji_rubies = []  # base has no kanji at all
    non_hira_rts = []     # rt contains non-hiragana
    suspicious_readings = []

    for base, rt in all_rubies:
        base_clean = base.strip()
        rt_clean = rt.strip()

        # Check if base has kanji
        has_kanji = bool(re.search(KANJI, base_clean))
        if not has_kanji:
            no_kanji_rubies.append((base_clean, rt_clean))
            continue

        # Okurigana leak: ends with hiragana
        if re.search(f'{HIRA}$', base_clean):
            okurigana_leaks.append((base_clean, rt_clean))

        # Prefix leak: starts with hiragana
        if re.search(f'^{HIRA}', base_clean):
            prefix_leaks.append((base_clean, rt_clean))

        # Non-hiragana rt
        if not re.match(r'^[ぁ-んー]+$', rt_clean):
            non_hira_rts.append((base_clean, rt_clean))

    return {
        'file': os.path.basename(fpath),
        'title': title,
        'title_rubies_count': len(title_rubies),
        'body_rubies_count': len(body_rubies),
        'nested_count': len(nested),
        'tag_errors': tag_errors,
        'okurigana_leaks': okurigana_leaks,
        'prefix_leaks': prefix_leaks,
        'no_kanji_rubies': no_kanji_rubies,
        'non_hira_rts': non_hira_rts,
    }

def main():
    post_files = sorted(glob.glob('content/posts/*.md'))
    manga_files = sorted(glob.glob('content/manga/*.md'))
    all_files = post_files + manga_files

    results = [analyze_post(f) for f in all_files]

    print("="*80)
    print(f"ANALYSIS OF {len(results)} POSTS & MANGA")
    print("="*80)

    # 1. Distribution of ruby counts
    universal_ruby_posts = [r for r in results if r['body_rubies_count'] > 50]
    light_ruby_posts = [r for r in results if 0 < r['body_rubies_count'] <= 50]
    title_only_posts = [r for r in results if r['body_rubies_count'] == 0 and r['title_rubies_count'] > 0]
    no_ruby_posts = [r for r in results if r['body_rubies_count'] == 0 and r['title_rubies_count'] == 0]

    print(f"\n[RUBY DISTRIBUTION]")
    print(f"- Full Universal Ruby Posts (body rubies > 50): {len(universal_ruby_posts)}")
    print(f"- Light Ruby Posts (1 - 50 body rubies): {len(light_ruby_posts)}")
    print(f"- Title-Only Ruby Posts (0 body rubies, title has ruby): {len(title_only_posts)}")
    print(f"- No Ruby Posts (0 in title & body): {len(no_ruby_posts)}")

    # 2. Tag Errors
    tag_error_posts = [r for r in results if r['tag_errors']]
    print(f"\n[TAG ERRORS] ({len(tag_error_posts)} files)")
    for r in tag_error_posts:
        print(f"  {r['file']}: {r['tag_errors']}")

    # 3. Nested Rubies
    nested_posts = [r for r in results if r['nested_count'] > 0]
    print(f"\n[ACTUAL NESTED RUBIES] ({len(nested_posts)} files)")
    for r in nested_posts:
        print(f"  {r['file']}: {r['nested_count']}")

    # 4. Okurigana Leaks (e.g. <ruby>食べる<rt>たべる</rt></ruby>)
    okuri_posts = [r for r in results if r['okurigana_leaks']]
    total_okuri = sum(len(r['okurigana_leaks']) for r in okuri_posts)
    print(f"\n[OKURIGANA LEAKS (送り仮名混入)] ({len(okuri_posts)} files, {total_okuri} instances)")
    # Show unique samples
    unique_okuri = {}
    for r in okuri_posts:
        for b, rt in r['okurigana_leaks']:
            unique_okuri[(b, rt)] = unique_okuri.get((b, rt), 0) + 1
    for (b, rt), cnt in sorted(unique_okuri.items(), key=lambda x: -x[1])[:20]:
        print(f"  <ruby>{b}<rt>{rt}</rt></ruby> (x{cnt})")

    # 5. Prefix Leaks (e.g. <ruby>お茶<rt>おちゃ</rt></ruby>)
    prefix_posts = [r for r in results if r['prefix_leaks']]
    total_prefix = sum(len(r['prefix_leaks']) for r in prefix_posts)
    print(f"\n[PREFIX LEAKS (接頭辞ひらがな混入)] ({len(prefix_posts)} files, {total_prefix} instances)")
    unique_prefix = {}
    for r in prefix_posts:
        for b, rt in r['prefix_leaks']:
            unique_prefix[(b, rt)] = unique_prefix.get((b, rt), 0) + 1
    for (b, rt), cnt in sorted(unique_prefix.items(), key=lambda x: -x[1])[:20]:
        print(f"  <ruby>{b}<rt>{rt}</rt></ruby> (x{cnt})")

    # 6. No Kanji in Base (e.g. <ruby>こと<rt>こと</rt></ruby>)
    no_kanji_posts = [r for r in results if r['no_kanji_rubies']]
    total_no_kanji = sum(len(r['no_kanji_rubies']) for r in no_kanji_posts)
    print(f"\n[NO KANJI IN BASE (漢字なし)] ({len(no_kanji_posts)} files, {total_no_kanji} instances)")
    for r in no_kanji_posts:
        print(f"  {r['file']}: {r['no_kanji_rubies']}")

    # 7. Non-Hiragana RT (e.g. katakana, symbols, etc.)
    non_hira_posts = [r for r in results if r['non_hira_rts']]
    total_non_hira = sum(len(r['non_hira_rts']) for r in non_hira_posts)
    print(f"\n[NON-HIRAGANA RT] ({len(non_hira_posts)} files, {total_non_hira} instances)")
    for r in non_hira_posts:
        print(f"  {r['file']}: {r['non_hira_rts']}")

    # List of title-only posts
    if title_only_posts:
        print(f"\n[TITLE-ONLY RUBY POSTS] ({len(title_only_posts)} files)")
        for r in title_only_posts:
            print(f"  {r['file']} (Title rubies: {r['title_rubies_count']})")

if __name__ == '__main__':
    main()
