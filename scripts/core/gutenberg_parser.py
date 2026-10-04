import os
import re
import sys

def format_inline_markdown(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    def link_repl(m):
        label = m.group(1)
        url = m.group(2)
        if url.endswith('.md'):
            basename = os.path.splitext(os.path.basename(url))[0]
            # Strip leading YYYY-MM-DD- if present
            slug = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', basename)
            return f'<a href="/{slug}/">{label}</a>'
        return f'<a href="{url}">{label}</a>'
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link_repl, text)
    return text

def parse_markdown_to_gutenberg_full(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    parts = re.split(r'^---\s*$', content, maxsplit=2, flags=re.MULTILINE)
    body = parts[2].strip() if len(parts) >= 3 else content.strip()

    lines = body.split('\n')
    blocks = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # HTML Block (e.g. <div class="c-dungeon-route">, <div class="c-vocab-box">)
        if stripped.startswith(('<div class="c-dungeon-route"', '<div class="c-vocab-box"')):
            div_lines = []
            depth = 0
            while i < len(lines):
                cur = lines[i]
                div_lines.append(cur)
                if '<div' in cur:
                    depth += cur.count('<div')
                if '</div>' in cur:
                    depth -= cur.count('</div>')
                if depth <= 0 and len(div_lines) > 1:
                    break
                i += 1
            div_html = "\n".join(div_lines)
            blocks.append(f"<!-- wp:html -->\n{div_html}\n<!-- /wp:html -->")
            i += 1
            continue

        # Details / Summary (<details>...</details>)
        if stripped.startswith('<details'):
            d_lines = []
            while i < len(lines):
                d_lines.append(lines[i])
                if '</details>' in lines[i]:
                    break
                i += 1
            d_html = "\n".join(d_lines)
            blocks.append(f"<!-- wp:html -->\n{d_html}\n<!-- /wp:html -->")
            i += 1
            continue

        # Code Block (``` ... ```)
        if stripped.startswith('```'):
            lang = stripped[3:].strip()
            c_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                c_lines.append(lines[i])
                i += 1
            code_text = "\n".join(c_lines)
            code_esc = code_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            blocks.append(f"<!-- wp:code -->\n<pre class=\"wp-block-code\"><code>{code_esc}</code></pre>\n<!-- /wp:code -->")
            i += 1
            continue

        # Separator (---)
        if stripped in ('---', '***', '___'):
            blocks.append('<!-- wp:separator -->\n<hr class="wp-block-separator has-alpha-channel-opacity" />\n<!-- /wp:separator -->')
            i += 1
            continue



        # Headings
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

        # Markdown Table (| ... |)
        if stripped.startswith('|') and '|' in stripped[1:]:
            tlines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                tlines.append(lines[i].strip())
                i += 1
            if len(tlines) >= 2:
                header_cols = [format_inline_markdown(c.strip()) for c in tlines[0].strip('|').split('|')]
                rows = []
                # Check if second line is separator like | :--- | :--- |
                start_row = 2 if re.match(r'^\|[\s\-:]+(\|[\s\-:]+)*\|?$', tlines[1]) else 1
                for row_line in tlines[start_row:]:
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

        # Image
        img_match = re.match(r'!\[(.*?)\]\((.*?)\)', stripped)
        if img_match:
            alt = img_match.group(1)
            src = img_match.group(2)
            if src.startswith('assets/'):
                src = f"https://nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/{src}"
            elif src.startswith('/assets/'):
                src = f"https://nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo{src}"
            fig = f"""<!-- wp:image {{"sizeSlug":"full","linkDestination":"none"}} -->
<figure class="wp-block-image size-full"><img src="{src}" alt="{alt}"/><figcaption class="wp-element-caption">{alt}</figcaption></figure>
<!-- /wp:image -->"""
            blocks.append(fig)
            i += 1
            continue

        # Shortcode
        if stripped.startswith('[oscss_'):
            blocks.append(f"<!-- wp:shortcode -->\n{stripped}\n<!-- /wp:shortcode -->")
            i += 1
            continue

        # Blockquote (Dialogues)
        if line.startswith('> '):
            qlines = []
            while i < len(lines) and lines[i].startswith('>'):
                raw_l = re.sub(r'^>\s?', '', lines[i])
                qlines.append(raw_l)
                i += 1

            dialogue_items = []
            current_speaker_icon = None
            current_speaker_name = None
            current_lines = []

            for ql in qlines:
                m = re.match(r'^([^\s*]+)\s*\*\*(.+?)\*\*[:：]\s*(.*)$', ql.strip())
                if m:
                    if current_speaker_name:
                        dialogue_items.append((current_speaker_icon, current_speaker_name, current_lines))
                    current_speaker_icon = m.group(1)
                    current_speaker_name = m.group(2)
                    current_lines = [m.group(3)] if m.group(3).strip() else []
                else:
                    if current_speaker_name:
                        current_lines.append(ql)
                    else:
                        current_lines.append(ql)

            if current_speaker_name:
                dialogue_items.append((current_speaker_icon, current_speaker_name, current_lines))

            if dialogue_items:
                for speaker_icon, speaker_name, speech_lines in dialogue_items:
                    clean_name = re.sub(r'<ruby>(.*?)<rt>.*?</rt></ruby>', r'\1', speaker_name)
                    is_oscar = "クルマ" in clean_name or "オスカー" in clean_name or speaker_icon in ("🚗", "👦", "👧")
                    
                    pos = "l" if is_oscar else "r"
                    avatar_class = "avatar-oscar" if is_oscar else "avatar-tanaka" if "田中" in clean_name else "avatar-staff"
                    avatar_url = "https://nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/my-icon.png" if is_oscar else "https://nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/avatar-staff.svg"

                    p_tags = "".join([f"<p>{format_inline_markdown(sl.strip())}</p>" for sl in speech_lines if sl.strip()])

                    balloon_html = f"""<div class="c-balloon c-balloon--{pos}">
  <div class="c-balloon__speaker">
    <div class="c-balloon__avatar {avatar_class}">
      <img src="{avatar_url}" alt="{clean_name}" loading="lazy" />
    </div>
    <span class="c-balloon__name">{clean_name}</span>
  </div>
  <div class="c-balloon__bubble">
    {p_tags}
  </div>
</div>"""
                    blocks.append(f"<!-- wp:html -->\n{balloon_html}\n<!-- /wp:html -->")
            else:
                box_lines = [format_inline_markdown(ql) for ql in qlines if ql.strip()]
                box_fmt = "<br />".join(box_lines)
                blocks.append(f"<!-- wp:quote -->\n<blockquote class=\"wp-block-quote\"><p>{box_fmt}</p></blockquote>\n<!-- /wp:quote -->")
            continue

        # Unordered List
        if line.startswith(('* ', '- ')):
            items = []
            while i < len(lines) and lines[i].strip().startswith(('* ', '- ')):
                item_content = re.sub(r'^[*\-]\s+', '', lines[i].strip())
                items.append(f"<li>{format_inline_markdown(item_content)}</li>")
                i += 1
            blocks.append(f"<!-- wp:list -->\n<ul>\n" + "\n".join(items) + "\n</ul>\n<!-- /wp:list -->")
            continue

        # Ordered List
        if re.match(r'^\d+\.\s+', stripped):
            items = []
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i].strip()):
                item_content = re.sub(r'^\d+\.\s+', '', lines[i].strip())
                items.append(f"<li>{format_inline_markdown(item_content)}</li>")
                i += 1
            blocks.append(f"<!-- wp:list {{\"ordered\":true}} -->\n<ol>\n" + "\n".join(items) + "\n</ol>\n<!-- /wp:list -->")
            continue

        # Paragraph
        p_lines = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(('#', '>', '---', '***', '___', '* ', '- ', '![', '|', '```', '<details', '<div')):
            if lines[i].strip().startswith('[oscss_') or re.match(r'^\d+\.\s+', lines[i].strip()):
                break
            p_lines.append(lines[i].strip())
            i += 1

        if p_lines:
            p_text = format_inline_markdown("<br />".join(p_lines))
            blocks.append(f"<!-- wp:paragraph -->\n<p>{p_text}</p>\n<!-- /wp:paragraph -->")
        else:
            i += 1

    return "\n\n".join(blocks)
