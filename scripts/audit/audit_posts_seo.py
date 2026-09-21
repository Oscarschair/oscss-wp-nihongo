import os
import re
import glob

posts_dir = "content/posts"
md_files = glob.glob(os.path.join(posts_dir, "*.md"))

results = []

for filepath in md_files:
    filename = os.path.basename(filepath)
    size = os.path.getsize(filepath)
    if size == 0:
        continue  # 空ファイルはスキップ
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 1. Frontmatter or direct markdown
    parts = re.split(r"^---\s*$", content, maxsplit=2, flags=re.MULTILINE)
    frontmatter = {}
    body = content
    if len(parts) >= 3 and parts[1].strip():
        fm_text = parts[1]
        body = parts[2]
        for line in fm_text.splitlines():
            line = line.strip()
            if ":" in line and not line.startswith("-"):
                k, v = line.split(":", 1)
                frontmatter[k.strip()] = v.strip().strip('"\'')
    
    title = frontmatter.get("title", "")
    if not title:
        h1_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        if h1_match:
            title = h1_match.group(1).strip()
            
    description = frontmatter.get("description", "")
    if not description:
        # Check first lead paragraph or blockquote
        lead_match = re.search(r"^>\s+.*?(こんにちは.*?)$", body, re.MULTILINE)
        if not lead_match:
            # First non-header paragraph
            paras = [p.strip() for p in body.split("\n\n") if p.strip() and not p.strip().startswith(("#", ">", "---"))]
            if paras:
                description = paras[0][:120]
        else:
            description = lead_match.group(1)[:120]

    # 2. Heading hierarchy check
    headings = re.findall(r"^(#{1,6})\s+(.+)$", body, re.MULTILINE)
    h_levels = [len(h[0]) for h in headings]
    heading_errors = []
    prev_level = 1
    for lvl in h_levels:
        if lvl > prev_level + 1 and lvl > 2:
            heading_errors.append(f"Jumped from h{prev_level} to h{lvl}")
        prev_level = lvl
    
    h1_count = len([lvl for lvl in h_levels if lvl == 1])
    h2_count = len([lvl for lvl in h_levels if lvl == 2])
    h3_count = len([lvl for lvl in h_levels if lvl == 3])
    
    # 3. Images and Alt text
    images = re.findall(r"!\[(.*?)\]\((.*?)\)", body)
    empty_alt_images = [img[1] for img in images if not img[0].strip()]
    
    # 4. Internal links
    internal_links = re.findall(r"\[(.*?)\]\((https?://nihongo\.oscarchair\.jp/.*?|/.*?)\)", body)
    rel_shortcode = re.findall(r'\[oscss_related\s+slug="([^"]+)"', body)
    
    # 5. Tables & Callouts & Rich elements
    has_table = bool(re.search(r"\|.+\|", body))
    has_quote = bool(re.search(r"^>\s+", body, re.MULTILINE))
    has_code_or_command = bool(re.search(r"```", body))
    
    # 6. Lengths
    title_len = len(title)
    desc_len = len(description)
    
    issues = []
    if title_len < 25 or title_len > 68:
        issues.append(f"Title: {title_len}文字 (推奨: 30〜60文字)")
    if desc_len < 60 or desc_len > 160:
        issues.append(f"Desc: {desc_len}文字 (推奨: 80〜140文字)")
    if heading_errors:
        issues.append(f"見出しジャンプ: {', '.join(heading_errors)}")
    if h1_count > 1:
        issues.append(f"h1タグが本文内に複数あり ({h1_count})")
    if empty_alt_images:
        issues.append(f"alt属性が空の画像 ({len(empty_alt_images)}枚)")
    if not internal_links and not rel_shortcode:
        issues.append("関連記事・内部リンク導線なし")

    results.append({
        "file": filename,
        "title": title,
        "title_len": title_len,
        "desc": description,
        "desc_len": desc_len,
        "h1": h1_count,
        "h2": h2_count,
        "h3": h3_count,
        "images": len(images),
        "links": len(internal_links) + len(rel_shortcode),
        "has_table": has_table,
        "has_quote": has_quote,
        "has_code": has_code_or_command,
        "issues": issues,
        "status": "PASS" if not issues else ("WARN" if len(issues) == 1 else "CHECK")
    })

print(f"監査対象: 実体のある投稿 {len(results)} 件")
print(f"完全合格 (PASS): {sum(1 for r in results if r['status'] == 'PASS')} 件")
print(f"軽微な改善余地 (WARN): {sum(1 for r in results if r['status'] == 'WARN')} 件")
print(f"要確認 (CHECK): {sum(1 for r in results if r['status'] == 'CHECK')} 件")
print("-" * 60)

import sys
sys.stdout.reconfigure(encoding='utf-8')

for r in results:
    icon = "[OK]" if r["status"] == "PASS" else ("[WARN]" if r["status"] == "WARN" else "[CHECK]")
    print(f"{icon} [{r['status']}] {r['file']}")
    print(f"   タイトル ({r['title_len']}文字): {r['title']}")
    print(f"   見出し構成: h1:{r['h1']} / h2:{r['h2']} / h3:{r['h3']} | 画像:{r['images']}枚 | 内部リンク:{r['links']}件 | 表:{'あり' if r['has_table'] else 'なし'}")
    if r["issues"]:
        print(f"   改善ポイント: {', '.join(r['issues'])}")
    print()
