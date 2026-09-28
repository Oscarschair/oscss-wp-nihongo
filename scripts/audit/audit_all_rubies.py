import glob
import os
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Kanji regex (including rare / joyo kanji)
KANJI_REGEX = re.compile(r'[\u4e00-\u9faf々〆ヵヶ]')
HIRA_REGEX = re.compile(r'^[ぁ-んー]+$')

def audit_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    issues = []
    
    # 1. Frontmatter checks
    parts = re.split(r'^---\s*$', content, maxsplit=2, flags=re.MULTILINE)
    frontmatter = parts[1] if len(parts) >= 3 else ""
    body = parts[2] if len(parts) >= 3 else content

    # Check slug for ruby
    for line in frontmatter.splitlines():
        if line.startswith('slug:') and '<ruby>' in line:
            issues.append(("FRONTMATTER_SLUG_RUBY", line))
        if line.startswith('thumbnail:') and '<ruby>' in line:
            issues.append(("FRONTMATTER_THUMBNAIL_RUBY", line))

    # 2. Tag balance & malformed tags
    open_ruby = len(re.findall(r'<ruby\b', content, re.IGNORECASE))
    close_ruby = len(re.findall(r'</ruby>', content, re.IGNORECASE))
    open_rt = len(re.findall(r'<rt\b', content, re.IGNORECASE))
    close_rt = len(re.findall(r'</rt>', content, re.IGNORECASE))

    if open_ruby != close_ruby:
        issues.append(("TAG_MISMATCH_RUBY", f"<ruby>: {open_ruby} vs </ruby>: {close_ruby}"))
    if open_rt != close_rt:
        issues.append(("TAG_MISMATCH_RT", f"<rt>: {open_rt} vs </rt>: {close_rt}"))
    if open_ruby != open_rt:
        issues.append(("TAG_MISMATCH_RUBY_RT", f"<ruby>: {open_ruby} vs <rt>: {open_rt}"))

    # Nested ruby
    nested_rubies = re.findall(r'<ruby[^>]*>.*?<ruby', content, re.DOTALL | re.IGNORECASE)
    if nested_rubies:
        issues.append(("NESTED_RUBY", f"Found {len(nested_rubies)} nested <ruby>"))

    # Empty ruby or rt
    empty_rubies = re.findall(r'<ruby>\s*<rt>\s*</rt>\s*</ruby>', content)
    if empty_rubies:
        issues.append(("EMPTY_RUBY", f"Found {len(empty_rubies)} empty rubies"))

    # 3. Ruby inside code blocks or backticks
    # Find all inline code `...`
    inline_codes = re.findall(r'`([^`\n]+)`', body)
    for code in inline_codes:
        if '<ruby>' in code:
            issues.append(("RUBY_IN_INLINE_CODE", code))

    # 4. Ruby inside URLs or markdown links URL part
    link_urls = re.findall(r'\]\(([^)\n]+)\)', body)
    for url in link_urls:
        if '<ruby>' in url:
            issues.append(("RUBY_IN_LINK_URL", url))

    # 5. Extract all <ruby>...</ruby> and inspect base vs rt
    ruby_matches = re.finditer(r'<ruby>(.*?)<rt>(.*?)</rt></ruby>', content, re.DOTALL)
    for m in ruby_matches:
        base = m.group(1).strip()
        rt = m.group(2).strip()

        # Check if base contains NO kanji at all
        if not KANJI_REGEX.search(base):
            issues.append(("NO_KANJI_IN_BASE", f"base='{base}', rt='{rt}'"))

        # Check if base starts or ends with hiragana (okurigana or prefix leaked into ruby)
        # e.g. <ruby>太る<rt>ふとる</rt></ruby> or <ruby>お冷<rt>おひや</rt></ruby>
        if re.search(r'^[ぁ-ん]', base) and KANJI_REGEX.search(base):
            issues.append(("HIRAGANA_PREFIX_IN_BASE", f"base='{base}', rt='{rt}'"))
        if re.search(r'[ぁ-ん]$', base) and KANJI_REGEX.search(base):
            issues.append(("HIRAGANA_SUFFIX_IN_BASE", f"base='{base}', rt='{rt}'"))

        # Check if base contains katakana, alphabet or symbols
        if re.search(r'[a-zA-Z0-9\s]', base):
            issues.append(("ALPHANUM_IN_BASE", f"base='{base}', rt='{rt}'"))

        # Check if rt is not pure hiragana (e.g. contains katakana, alphabet, kanji, or punctuation)
        if not HIRA_REGEX.match(rt):
            issues.append(("NON_HIRAGANA_RT", f"base='{base}', rt='{rt}'"))

        # Check if base and rt are identical (redundant ruby)
        if base == rt:
            issues.append(("IDENTICAL_BASE_RT", f"base='{base}', rt='{rt}'"))

    return issues

def main():
    post_files = sorted(glob.glob('content/posts/*.md'))
    manga_files = sorted(glob.glob('content/manga/*.md'))
    all_files = post_files + manga_files

    print(f"Total files to inspect: {len(all_files)}")
    
    total_issues_count = 0
    files_with_issues = 0
    issue_type_counter = {}

    for fpath in all_files:
        issues = audit_file(fpath)
        if issues:
            files_with_issues += 1
            print(f"\n[{os.path.basename(fpath)}] - {len(issues)} issues found:")
            for itype, idesc in issues:
                issue_type_counter[itype] = issue_type_counter.get(itype, 0) + 1
                total_issues_count += 1
                print(f"  - [{itype}] {idesc}")

    print("\n" + "="*50)
    print("AUDIT SUMMARY:")
    print(f"Total files audited: {len(all_files)}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Total issue instances: {total_issues_count}")
    print("Issues by type:")
    for itype, count in sorted(issue_type_counter.items(), key=lambda x: -x[1]):
        print(f"  {itype}: {count}")

if __name__ == '__main__':
    main()
