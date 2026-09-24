import glob
import html
import json
import os
import re
import sys
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def format_inline_markdown(text):
    if not text:
        return ""
    # 1. Links: [text](url) -> <a href="url">text</a>
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    # 2. Bold: **text** -> <strong>text</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # 3. Italic: *text* -> <em>text</em>
    text = re.sub(r'(?<!\*)\*([^\*]+?)\*(?!\*)', r'<em>\1</em>', text)
    # 4. Inline code: `code` -> <code>code</code>
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # 5. Clean up any stray dangling asterisks
    text = text.replace('**', '')
    return text

def md_to_gutenberg(md_text):
    body = re.sub(r'^---[\s\S]*?---', '', md_text).strip()
    body = re.sub(r'^#\s+.*?\n+', '', body).strip()
    
    lines = body.split('\n')
    blocks = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        # 0. Code block (```)
        if line.startswith('```'):
            codelines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                codelines.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1 # skip closing ```
            
            raw_joined = "\n".join(codelines)
            # Check if this is an RPG command block (contains 【, コマンド, ▶, or ➔)
            if any(k in raw_joined for k in ['【', 'コマンド', '▶', '➔']):
                cmd_title = ""
                items = []
                for cl in codelines:
                    cl_str = cl.strip()
                    if not cl_str or re.match(r'^-+$', cl_str):
                        continue
                    if cl_str.startswith('【') and '】' in cl_str:
                        cmd_title = format_inline_markdown(cl_str)
                    elif cl_str.startswith('▶'):
                        item_content = re.sub(r'^▶\s*', '', cl_str)
                        items.append(format_inline_markdown(item_content))
                    else:
                        items.append(format_inline_markdown(cl_str))
                
                title_html = f'<div class="c-command-box__title">{cmd_title}</div>' if cmd_title else ''
                items_html = "\n".join([f'<li class="c-command-box__item"><span class="c-command-box__cursor">▶</span><span>{it}</span></li>' for it in items])
                cmd_box_html = f'<div class="c-command-box">\n  {title_html}\n  <ul class="c-command-box__list">\n{items_html}\n  </ul>\n</div>'
                blocks.append(f"<!-- wp:html -->\n{cmd_box_html}\n<!-- /wp:html -->")
            else:
                code_content = html.escape(raw_joined)
                blocks.append(f"<!-- wp:preformatted -->\n<pre class=\"wp-block-preformatted\">{code_content}</pre>\n<!-- /wp:preformatted -->")
            continue

        # 1. Blockquote / Dialogue (> ...)
        if line.startswith('>'):
            qlines = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                cleaned = re.sub(r'^>\s?', '', lines[i].strip())
                if cleaned:
                    qlines.append(cleaned)
                i += 1
            
            # Helper: Parse a line for speaker and content
            def parse_dialogue_line(raw_line):
                l = raw_line.strip()
                # Pattern 1: **Speaker: Content** (entire line bold)
                m = re.match(r'^\*\*(.+?)(?:：|:)\s*(.+?)\*\*$', l)
                if m:
                    return m.group(1).strip(), m.group(2).strip()
                # Pattern 2: **Speaker：** Content
                m = re.match(r'^\*\*(.+?)(?:：|:)\*\*\s*(.*)$', l)
                if m:
                    return m.group(1).strip(), m.group(2).strip()
                # Pattern 3: **Speaker**： Content
                m = re.match(r'^\*\*(.+?)\*\*(?:：|:)\s*(.*)$', l)
                if m:
                    return m.group(1).strip(), m.group(2).strip()
                # Pattern 4: <strong>Speaker</strong>： Content
                m = re.match(r'^<strong>(.+?)</strong>(?:：|:)\s*(.*)$', l)
                if m:
                    return m.group(1).strip(), m.group(2).strip()
                # Pattern 5: 💬 **Speaker** or 💬 Speaker
                m = re.match(r'^(?:💬\s*)?\*\*(.+?)\*\*\s*$', l)
                if m and any(k in m.group(1) for k in ['オスカー', 'あなた', '店員', '私', '同僚', '取引先', '美容師']):
                    return m.group(1).strip(), ''
                return None, None

            # Check if this blockquote contains dialogue
            dialogue_items = []
            current_speaker = None
            current_content_lines = []

            for ql in qlines:
                sp, ct = parse_dialogue_line(ql)
                if sp:
                    if current_speaker:
                        dialogue_items.append((current_speaker, current_content_lines))
                    current_speaker = sp
                    current_content_lines = [ct] if ct else []
                else:
                    if current_speaker:
                        current_content_lines.append(ql)
                    else:
                        # Non-dialogue line before any speaker
                        pass

            if current_speaker:
                dialogue_items.append((current_speaker, current_content_lines))

            if dialogue_items:
                # Output individual speech balloons for each speaker turn
                for sp, ct_lines in dialogue_items:
                    # Clean speaker name from icons or emojis
                    clean_sp = re.sub(r'^[💬💡🗣️\s]+', '', sp).strip()
                    clean_sp_plain = html.escape(re.sub(r'<[^>]+>', '', clean_sp))
                    
                    # Determine avatar and position
                    if any(k in clean_sp for k in ['オスカー', 'あなた', '私', '僕', '客側', '本音']):
                        position = "l"
                        avatar = "https://nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/my-icon.png"
                    else:
                        position = "r"
                        avatar = "https://nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/avatar-staff.svg"
                    
                    # Split ct_lines by empty lines into paragraphs for proper line-height calculation
                    paragraphs = []
                    current_p = []
                    for bl in ct_lines:
                        if not bl.strip():
                            if current_p:
                                paragraphs.append("<br />".join(current_p))
                                current_p = []
                        else:
                            current_p.append(format_inline_markdown(bl))
                    if current_p:
                        paragraphs.append("<br />".join(current_p))
                    
                    if not paragraphs:
                        paragraphs = [""]
                    
                    p_tags = "\n    ".join([f"<p>{p}</p>" for p in paragraphs])
                    
                    balloon_html = f"""<div class="c-balloon c-balloon--{position}">
  <div class="c-balloon__speaker">
    <img src="{avatar}" alt="{clean_sp_plain}" class="c-balloon__avatar" loading="lazy" />
    <span class="c-balloon__name">{clean_sp}</span>
  </div>
  <div class="c-balloon__bubble">
    {p_tags}
  </div>
</div>"""
                    blocks.append(f"<!-- wp:html -->\n{balloon_html}\n<!-- /wp:html -->")
            else:
                # Normal quote / information box
                box_lines = [format_inline_markdown(ql) for ql in qlines]
                box_fmt = "<br />".join(box_lines)
                blocks.append(f"<!-- wp:quote -->\n<blockquote class=\"wp-block-quote\"><p>{box_fmt}</p></blockquote>\n<!-- /wp:quote -->")
            continue

        # 1.8. Vocabulary Section (## 🎯 今回の語彙)
        if line.startswith('## 🎯 今回の語彙') or line.startswith('## 今回の語彙'):
            v_title = format_inline_markdown(re.sub(r'^##\s*', '', line).strip())
            i += 1
            lead_text = ""
            vocab_items = []
            current_item = None
            
            while i < len(lines):
                cur = lines[i].strip()
                if not cur:
                    i += 1
                    continue
                if cur.startswith(('## ', '### ', '---', '***', '___')):
                    break
                
                # Check if this line is a main vocabulary entry: e.g. * **温泉（おんせん）** 【JLPT N2】
                # Can start with '* **' or '- **'
                if (cur.startswith('* **') or cur.startswith('- **')) and ('【' in cur or 'JLPT' in cur):
                    if current_item:
                        vocab_items.append(current_item)
                    
                    w_match = re.search(r'\*\*(.+?)\*\*\s*【(?:JLPT\s*)?([Nn][1-5])】', cur)
                    if w_match:
                        word_and_reading = w_match.group(1).strip()
                        jlpt_lvl = w_match.group(2).upper()
                    else:
                        item_text = re.sub(r'^[*\-]\s+', '', cur).strip()
                        word_and_reading = re.sub(r'\*+', '', item_text).strip()
                        jlpt_lvl = "N3"
                    
                    current_item = {
                        "word": word_and_reading,
                        "jlpt": jlpt_lvl,
                        "meaning": "",
                        "example": ""
                    }
                    i += 1
                    continue
                
                # Sub-attributes (意味 / 例文) or lead text
                if current_item:
                    clean_line = re.sub(r'^[*\-\s]+', '', cur).strip()
                    if '意味：' in clean_line or '意味:' in clean_line:
                        current_item["meaning"] = re.sub(r'^意味[：:]\s*', '', clean_line).strip()
                    elif '例文：' in clean_line or '例文:' in clean_line:
                        current_item["example"] = re.sub(r'^例文[：:]\s*', '', clean_line).strip()
                    else:
                        if not current_item["meaning"]:
                            current_item["meaning"] = clean_line
                        elif not current_item["example"]:
                            current_item["example"] = clean_line
                        else:
                            current_item["example"] += " " + clean_line
                else:
                    if not lead_text:
                        lead_text = format_inline_markdown(cur)
                    else:
                        lead_text += "<br>" + format_inline_markdown(cur)
                i += 1
            
            if current_item:
                vocab_items.append(current_item)
            
            vocab_cards = []
            for item in vocab_items:
                badge_cls = f"c-badge--jlpt-{item['jlpt'].lower()}"
                card_html = f"""    <div class="c-vocab-card">
      <div class="c-vocab-card__header">
        <span class="c-vocab-card__word">{item['word']}</span>
        <span class="c-badge c-badge--jlpt {badge_cls}">JLPT {item['jlpt']}</span>
      </div>
      <p class="c-vocab-card__meaning"><strong>意味：</strong>{format_inline_markdown(item['meaning'])}</p>
      <p class="c-vocab-card__example"><strong>例文：</strong>{format_inline_markdown(item['example'])}</p>
    </div>"""
                vocab_cards.append(card_html)
            
            lead_html = f'<p class="c-vocab-box__lead">{lead_text}</p>' if lead_text else ''
            cards_joined = "\n".join(vocab_cards)
            box_html = f"""<div class="c-vocab-box">
  <h3 class="c-vocab-box__title">{v_title}</h3>
  {lead_html}
  <div class="c-vocab-grid">
{cards_joined}
  </div>
</div>"""
            blocks.append(f"<!-- wp:html -->\n{box_html}\n<!-- /wp:html -->")
            continue

        # 2. Headings
        if line.startswith('## '):
            h_text = format_inline_markdown(line[3:].strip())
            blocks.append(f"<!-- wp:heading -->\n<h2 class=\"wp-block-heading\">{h_text}</h2>\n<!-- /wp:heading -->")
            i += 1
            continue
        if line.startswith('### '):
            h_text = format_inline_markdown(line[4:].strip())
            blocks.append(f"<!-- wp:heading {{\"level\":3}} -->\n<h3 class=\"wp-block-heading\">{h_text}</h3>\n<!-- /wp:heading -->")
            i += 1
            continue
        if line.startswith('#### '):
            h_text = format_inline_markdown(line[5:].strip())
            blocks.append(f"<!-- wp:heading {{\"level\":4}} -->\n<h4 class=\"wp-block-heading\">{h_text}</h4>\n<!-- /wp:heading -->")
            i += 1
            continue

        # 3. Horizontal Separator
        if line in ['---', '***', '___']:
            blocks.append("<!-- wp:separator -->\n<hr class=\"wp-block-separator has-alpha-channel-opacity\"/>\n<!-- /wp:separator -->")
            i += 1
            continue

        # 4. Images
        if line.startswith('!['):
            m = re.match(r'^!\[(.*?)\]\((.*?)\)', line)
            if m:
                alt_text, img_url = m.groups()
                if not img_url.startswith(('http://', 'https://')):
                    clean_rel = img_url.lstrip('/')
                    img_url = f"https://nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/{clean_rel}"
                blocks.append(f"""<!-- wp:image {{"sizeSlug":"large","linkDestination":"none"}} -->
<figure class="wp-block-image size-large"><img src="{img_url}" alt="{alt_text}"/><figcaption class="wp-element-caption">{alt_text}</figcaption></figure>
<!-- /wp:image -->""")
            i += 1
            continue

        # 5. Tables
        if line.startswith('|'):
            tlines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                tlines.append(lines[i].strip())
                i += 1
            if len(tlines) >= 2:
                header_cols = [format_inline_markdown(c.strip()) for c in tlines[0].strip('|').split('|')]
                rows = []
                for row_line in tlines[2:]:
                    cols = [format_inline_markdown(c.strip()) for c in row_line.strip('|').split('|')]
                    rows.append(cols)
                table_html = "<figure class=\"wp-block-table c-article-table-wrap\"><table class=\"c-article-table\"><thead><tr>"
                for h in header_cols:
                    table_html += f"<th>{h}</th>"
                table_html += "</tr></thead><tbody>"
                for row in rows:
                    table_html += "<tr>"
                    for cell in row:
                        table_html += f"<td>{cell}</td>"
                    table_html += "</tr>"
                table_html += "</tbody></table></figure>"
                blocks.append(f"<!-- wp:table {{\"className\":\"c-article-table-wrap\"}} -->\n{table_html}\n<!-- /wp:table -->")
            continue

        # 6. Shortcode block ([...])
        if line.startswith('[') and line.endswith(']') and not line.startswith('[!'):
            blocks.append(f"<!-- wp:shortcode -->\n{line}\n<!-- /wp:shortcode -->")
            i += 1
            continue

        # 7. Unordered Lists (Supports multi-line items with descriptions)
        if line.startswith('* ') or line.startswith('- '):
            items = []
            while i < len(lines):
                cur_line = lines[i].strip()
                if not cur_line:
                    peek = i + 1
                    while peek < len(lines) and not lines[peek].strip():
                        peek += 1
                    if peek < len(lines) and (lines[peek].strip().startswith('* ') or lines[peek].strip().startswith('- ')):
                        i += 1
                        continue
                    else:
                        break
                
                if cur_line.startswith('* ') or cur_line.startswith('- '):
                    item_head = format_inline_markdown(cur_line[2:])
                    item_parts = [item_head]
                    i += 1
                    while i < len(lines):
                        sub_line = lines[i].strip()
                        if not sub_line:
                            peek = i + 1
                            while peek < len(lines) and not lines[peek].strip():
                                peek += 1
                            if peek < len(lines) and (lines[peek].strip().startswith('* ') or lines[peek].strip().startswith('- ')):
                                break
                            elif peek < len(lines) and (lines[peek].strip().startswith(('#', '>', '|', '---', '***', '___', '![', '```')) or re.match(r'^\d+\.\s+', lines[peek].strip())):
                                break
                            else:
                                i += 1
                                continue
                        
                        if sub_line.startswith('* ') or sub_line.startswith('- ') or sub_line.startswith(('#', '>', '|', '---', '***', '___', '![', '```')) or re.match(r'^\d+\.\s+', sub_line):
                            break
                        
                        item_parts.append(format_inline_markdown(sub_line))
                        i += 1
                    
                    item_content = "<br />".join([p for p in item_parts if p])
                    items.append(item_content)
                else:
                    break
            
            blocks.append("<!-- wp:list -->\n<ul>" + "".join([f"<li>{it}</li>" for it in items]) + "</ul>\n<!-- /wp:list -->")
            continue

        # 8. Ordered Lists (Supports multi-line items with descriptions)
        if re.match(r'^\d+\.\s+', line):
            items = []
            while i < len(lines):
                cur_line = lines[i].strip()
                if not cur_line:
                    peek = i + 1
                    while peek < len(lines) and not lines[peek].strip():
                        peek += 1
                    if peek < len(lines) and re.match(r'^\d+\.\s+', lines[peek].strip()):
                        i += 1
                        continue
                    else:
                        break
                
                m = re.match(r'^\d+\.\s+(.*)', cur_line)
                if m:
                    item_head = format_inline_markdown(m.group(1))
                    item_parts = [item_head]
                    i += 1
                    while i < len(lines):
                        sub_line = lines[i].strip()
                        if not sub_line:
                            peek = i + 1
                            while peek < len(lines) and not lines[peek].strip():
                                peek += 1
                            if peek < len(lines) and re.match(r'^\d+\.\s+', lines[peek].strip()):
                                break
                            elif peek < len(lines) and (lines[peek].strip().startswith(('#', '>', '|', '---', '***', '___', '![', '* ', '- ', '```')) or (lines[peek].strip().startswith('[') and lines[peek].strip().endswith(']'))):
                                break
                            else:
                                i += 1
                                continue
                        
                        if re.match(r'^\d+\.\s+', sub_line) or sub_line.startswith(('#', '>', '|', '---', '***', '___', '![', '* ', '- ', '```')) or (sub_line.startswith('[') and sub_line.endswith(']')):
                            break
                        
                        item_parts.append(format_inline_markdown(sub_line))
                        i += 1
                    
                    item_content = "<br />".join([p for p in item_parts if p])
                    items.append(item_content)
                else:
                    break
            
            blocks.append("<!-- wp:list {\"ordered\":true} -->\n<ol>" + "".join([f"<li>{it}</li>" for it in items]) + "</ol>\n<!-- /wp:list -->")
            continue

        # 9. Regular Paragraph (Fallback)
        plines = []
        while i < len(lines):
            cur = lines[i].strip()
            if not cur or cur.startswith(('#', '>', '|', '---', '***', '___', '![', '* ', '- ', '```')) or re.match(r'^\d+\.\s+', cur) or (cur.startswith('[') and cur.endswith(']') and not cur.startswith('[!')):
                break
            plines.append(cur)
            i += 1
            
        if plines:
            plines_formatted = [format_inline_markdown(p) for p in plines]
            p_text = "<br />".join(plines_formatted)
            blocks.append(f"<!-- wp:paragraph -->\n<p>{p_text}</p>\n<!-- /wp:paragraph -->")
        else:
            i += 1

    return "\n\n".join(blocks)

# 記事リストを読み込んで Gutenberg HTML に変換
posts_dir = "content/posts"
files = sorted(glob.glob(os.path.join(posts_dir, "*.md")))
if len(sys.argv) > 1 and sys.argv[1].strip():
    filter_arg = sys.argv[1].strip()
    files = [f for f in files if filter_arg in f]
    print(f"Filtered files by '{filter_arg}': {len(files)} files matched.")

updates = []
for fpath in files:
    if os.path.getsize(fpath) == 0:
        continue
    with open(fpath, "r", encoding="utf-8") as fp:
        c = fp.read()
        
    parts = re.split(r"^---\s*$", c, maxsplit=2, flags=re.MULTILINE)
    if len(parts) >= 3:
        fm = parts[1]
        slug_match = re.search(r'slug:\s*["\']?([^"\']+)["\']?', fm)
        title_match = re.search(r'title:\s*["\'](.*?)["\']\s*$', fm, flags=re.MULTILINE)
        if not title_match:
            title_match = re.search(r'title:\s*(.+)$', fm, flags=re.MULTILINE)
        desc_match = re.search(r'description:\s*["\']?([^"\']+)["\']?', fm)
        date_match = re.search(r'date:\s*["\']?([^"\']+)["\']?', fm)
        thumb_match = re.search(r'thumbnail:\s*["\']?([^"\']+)["\']?', fm)
        jlpt_match = re.search(r'jlpt:\s*["\']?([^"\']+)["\']?', fm)

        # Categories extraction
        cats = []
        cat_block = re.search(r'categories:\s*\n((?:\s*-\s*[^\n]+\n?)+)', fm)
        if cat_block:
            cats = [re.sub(r'["\']', '', l.replace('-', '').strip()) for l in cat_block.group(1).strip().split('\n') if l.strip()]

        # Tags extraction
        tags = []
        tag_block = re.search(r'tags:\s*\n((?:\s*-\s*[^\n]+\n?)+)', fm)
        if tag_block:
            tags = [re.sub(r'["\']', '', l.replace('-', '').strip()) for l in tag_block.group(1).strip().split('\n') if l.strip()]

        if slug_match:
            slug = slug_match.group(1).strip()
            title = title_match.group(1).strip() if title_match else ""
            desc = desc_match.group(1).strip() if desc_match else ""
            date_val = date_match.group(1).strip() if date_match else ""
            thumb_path = thumb_match.group(1).strip() if thumb_match else ""
            jlpt_val = jlpt_match.group(1).strip() if jlpt_match else ""

            # タイトルルール強制ガード: カテゴリプレフィックスが漏れている場合の自動付与
            expected_prefix = None
            if slug.startswith('culture-shock') or (cats and 'カルチャー' in cats[0]):
                expected_prefix = 'カルチャーショック：'
            elif slug.startswith('street-japanese') or slug.startswith('street-') or (cats and ('街角' in cats[0] or 'サバイバル' in cats[0])):
                expected_prefix = '街角サバイバル：'
            elif slug.startswith('kotoba-no-aya') or (cats and 'ことば' in cats[0]):
                expected_prefix = 'ことばのあや：'
            elif slug.startswith('japanese-comparing') or 'comparing' in slug or (cats and ('くらべて' in cats[0] or '納得' in cats[0])):
                expected_prefix = 'くらべてみました：'

            if expected_prefix:
                clean_t = title
                # 既存の各種プレフィックス（ルビ付き・表記揺れ含む）を除去
                prefixes_to_clean = [
                    r'^(?:<ruby>街角<rt>.*?</rt></ruby>|街角)サバイバル[：:]\s*',
                    r'^街角サバイバル[：:]\s*',
                    r'^(?:<ruby>言葉<rt>.*?</rt></ruby>|ことば)のあや[：:]\s*',
                    r'^ことばのあや[：:]\s*',
                    r'^カルチャーショック[：:]\s*',
                    r'^くらべてみました[：:]\s*',
                    r'^くらべて<ruby>納得<rt>.*?</rt></ruby>[！!]?[：:]\s*',
                    r'^くらべて納得[！!]?[：:]\s*',
                ]
                for p_pat in prefixes_to_clean:
                    clean_t = re.sub(p_pat, '', clean_t)
                title = f"{expected_prefix}{clean_t}"

            html_body = md_to_gutenberg(c)
            updates.append({
                "slug": slug,
                "title": title,
                "desc": desc,
                "date": date_val,
                "cats": cats,
                "tags": tags,
                "thumb_path": thumb_path,
                "jlpt": jlpt_val,
                "html": html_body
            })

print(f"Prepared {len(updates)} posts with Gutenberg HTML blocks.")

# SSH接続して一括更新
env_data = {}
with open('.env.deploy', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env_data[k.strip()] = v.strip()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    hostname=env_data['SSH_HOST'],
    port=int(env_data['SSH_PORT']),
    username=env_data['SSH_USER'],
    password=env_data['SSH_PASS'],
    look_for_keys=False,
    allow_agent=False
)
sftp = ssh.open_sftp()

theme_dir = "web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo"
remote_json = f"{theme_dir}/gutenberg_updates.json.gz"
remote_php = f"{theme_dir}/repair_gutenberg.php"

import gzip
tmp_json_gz = 'gutenberg_updates_tmp.json.gz'
with gzip.open(tmp_json_gz, 'wb') as f:
    f.write(json.dumps(updates, ensure_ascii=False).encode('utf-8'))
sftp.put(tmp_json_gz, remote_json)
if os.path.exists(tmp_json_gz):
    os.remove(tmp_json_gz)

php_script = r'''<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');

$raw = file_get_contents(__DIR__ . '/gutenberg_updates.json.gz');
$data = json_decode(gzdecode($raw), true);

$updated = 0;
$created = 0;

foreach ($data as $item) {
    $slug = $item['slug'];
    $posts = get_posts(array(
        'name' => $slug,
        'post_type' => 'post',
        'post_status' => array('publish', 'future', 'draft', 'pending'),
        'numberposts' => 1
    ));

    // カテゴリーIDの特定
    $cat_ids = array();
    $cat_map = array(
        '街角サバイバル' => 7,
        '街角日本語サバイバル' => 7,
        '街角日本語' => 7,
        'street-survival' => 7,
        'street-japanese' => 7,
        'くらべてみました' => 2,
        'くらべて納得！' => 2,
        'くらべて納得' => 2,
        'comparing' => 2,
        'comparing-japanese' => 2,
        'ことばのあや' => 4,
        'kotoba-no-aya' => 4,
        'カルチャーショック' => 5,
        'カルチャーショック！' => 5,
        'culture-shock' => 5,
    );
    if (!empty($item['cats'])) {
        foreach ($item['cats'] as $cval) {
            $cval_clean = trim(str_replace(array('"', "'", '！', '!'), '', $cval));
            if (isset($cat_map[$cval])) {
                $cat_ids[] = $cat_map[$cval];
                continue;
            }
            if (isset($cat_map[$cval_clean])) {
                $cat_ids[] = $cat_map[$cval_clean];
                continue;
            }
            $cat_obj = get_category_by_slug($cval);
            if ($cat_obj) {
                $cat_ids[] = $cat_obj->term_id;
                continue;
            }
            $cat_obj = get_term_by('name', $cval, 'category');
            if ($cat_obj) {
                $cat_ids[] = $cat_obj->term_id;
                continue;
            }
        }
    }
    // フォールバック: スラッグプレフィックスから特定
    if (empty($cat_ids)) {
        if (strpos($slug, 'street-japanese') !== false || strpos($slug, 'street-') !== false) {
            $cat_ids[] = 7;
        } elseif (strpos($slug, 'culture-shock') !== false) {
            $cat_ids[] = 5;
        } elseif (strpos($slug, 'comparing') !== false) {
            $cat_ids[] = 2;
        } elseif (strpos($slug, 'kotoba-no-aya') !== false) {
            $cat_ids[] = 4;
        }
    }
    $cat_ids = array_values(array_unique($cat_ids));

    // アイキャッチ画像の取得/登録
    $thumb_id = 0;
    if (!empty($item['thumb_path'])) {
        $full_thumb_path = getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/' . $item['thumb_path'];
        if (file_exists($full_thumb_path)) {
            $existing_attach = get_posts(array(
                'post_type' => 'attachment',
                'meta_key' => '_wp_attached_file',
                'meta_value' => basename($full_thumb_path),
                'numberposts' => 1
            ));
            if (!empty($existing_attach)) {
                $thumb_id = $existing_attach[0]->ID;
            } else {
                $upload_dir = wp_upload_dir();
                $dest_file = $upload_dir['path'] . '/' . basename($full_thumb_path);
                copy($full_thumb_path, $dest_file);
                $filetype = wp_check_filetype(basename($full_thumb_path), null);
                $attachment = array(
                    'guid'           => $upload_dir['url'] . '/' . basename($full_thumb_path),
                    'post_mime_type' => $filetype['type'],
                    'post_title'     => preg_replace('/\.[^.]+$/', '', basename($full_thumb_path)),
                    'post_content'   => '',
                    'post_status'    => 'inherit'
                );
                $thumb_id = wp_insert_attachment($attachment, $dest_file);
                $attach_data = wp_generate_attachment_metadata($thumb_id, $dest_file);
                wp_update_attachment_metadata($thumb_id, $attach_data);
            }
        }
    }

    if (!empty($posts)) {
        $p = $posts[0];
        $post_arr = array(
            'ID'           => $p->ID,
            'post_content' => $item['html']
        );
        if (!empty($item['title'])) {
            $post_arr['post_title'] = $item['title'];
        }
        if (!empty($item['desc'])) {
            $post_arr['post_excerpt'] = $item['desc'];
        }
        if (!empty($cat_ids)) {
            $post_arr['post_category'] = $cat_ids;
        }
        if (!empty($item['date'])) {
            $post_date = substr(str_replace('T', ' ', $item['date']), 0, 19);
            $post_status = (strtotime($post_date) > current_time('timestamp')) ? 'future' : 'publish';
            $post_arr['post_date'] = $post_date;
            $post_arr['post_date_gmt'] = get_gmt_from_date($post_date);
            $post_arr['post_status'] = $post_status;
        }
        wp_update_post($post_arr);

        // sanitize_post / kses による <ruby> や HTMLタグのエスケープ・除去を回避し、正本として直接保存
        global $wpdb;
        $update_fields = array(
            'post_content' => $item['html']
        );
        if (!empty($item['title'])) {
            $update_fields['post_title'] = $item['title'];
        }
        $wpdb->update(
            $wpdb->posts,
            $update_fields,
            array('ID' => $p->ID)
        );
        clean_post_cache($p->ID);

        if (!empty($cat_ids)) {
            wp_set_post_categories($p->ID, $cat_ids);
        }

        if (!empty($item['tags'])) {
            wp_set_post_tags($p->ID, $item['tags'], false);
        }

        if ($thumb_id > 0) {
            set_post_thumbnail($p->ID, $thumb_id);
        }
        if (!empty($item['jlpt'])) {
            update_post_meta($p->ID, '_oscss_jlpt_level', $item['jlpt']);
        }
        echo "Successfully repaired post ID: {$p->ID} (slug: {$slug}, cats: " . implode(',', $cat_ids) . ")\n";
        $updated++;
    } else {
        // 新規投稿の作成
        $post_date = !empty($item['date']) ? substr(str_replace('T', ' ', $item['date']), 0, 19) : current_time('mysql');
        $post_status = (strtotime($post_date) > current_time('timestamp')) ? 'future' : 'publish';

        $new_post = array(
            'post_title'    => !empty($item['title']) ? $item['title'] : $slug,
            'post_name'     => $slug,
            'post_content'  => $item['html'],
            'post_excerpt'  => !empty($item['desc']) ? $item['desc'] : '',
            'post_status'   => $post_status,
            'post_date'     => $post_date,
            'post_date_gmt' => get_gmt_from_date($post_date),
            'post_category' => $cat_ids,
            'tags_input'    => !empty($item['tags']) ? $item['tags'] : array()
        );
        $new_id = wp_insert_post($new_post);
        if (!is_wp_error($new_id) && $new_id > 0) {
            global $wpdb;
            $update_fields = array(
                'post_content' => $item['html']
            );
            if (!empty($item['title'])) {
                $update_fields['post_title'] = $item['title'];
            }
            $wpdb->update(
                $wpdb->posts,
                $update_fields,
                array('ID' => $new_id)
            );
            clean_post_cache($new_id);
            update_post_meta($new_id, '_oscss_post_views', 0);
            if (!empty($item['jlpt'])) {
                update_post_meta($new_id, '_oscss_jlpt_level', $item['jlpt']);
            }
            if ($thumb_id > 0) {
                set_post_thumbnail($new_id, $thumb_id);
            }
            echo "Successfully created NEW post ID: {$new_id} (slug: {$slug}, status: {$post_status}, date: {$post_date})\n";
            $created++;
        } else {
            echo "Error creating post for slug: {$slug}\n";
        }
    }
}
echo "Total posts repaired: {$updated}, Newly created: {$created}\n";

// OPcache, LiteSpeed, Object Cache パージ
if (function_exists('opcache_reset')) { opcache_reset(); }
if (class_exists('LiteSpeed\\Purge')) { 
    \LiteSpeed\Purge::purge_all(); 
}
do_action('litespeed_purge_all');
wp_cache_flush();

echo "All caches purged successfully!\n";
?>'''

tmp_php = 'repair_gutenberg_tmp.php'
with open(tmp_php, 'w', encoding='utf-8') as f:
    f.write(php_script)
sftp.put(tmp_php, remote_php)
if os.path.exists(tmp_php):
    os.remove(tmp_php)

stdin, stdout, stderr = ssh.exec_command(f'LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php $HOME/{remote_php} && rm -f $HOME/{remote_php} $HOME/{remote_json}')
out = stdout.read().decode('utf-8', errors='ignore')
err = stderr.read().decode('utf-8', errors='ignore')
print("OUTPUT:\n", out)
if err:
    print("ERR:\n", err)

sftp.close()
ssh.close()
print("Post repair and cache purge completed.")
