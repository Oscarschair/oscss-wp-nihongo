import os
import re
import sys
import json
import base64
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

def format_inline_markdown(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text

def parse_markdown_to_gutenberg(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split frontmatter
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

        # HTML Block (e.g. <div class="c-dungeon-route">)
        if stripped.startswith('<div class="c-dungeon-route"'):
            div_lines = []
            while i < len(lines):
                div_lines.append(lines[i])
                if '</div>' in lines[i] and len(div_lines) > 5:
                    break
                i += 1
            div_html = "\n".join(div_lines)
            blocks.append(f"<!-- wp:html -->\n{div_html}\n<!-- /wp:html -->")
            i += 1
            continue

        # Separator (---)
        if stripped in ('---', '***', '___'):
            blocks.append('<!-- wp:separator -->\n<hr class="wp-block-separator has-alpha-channel-opacity" />\n<!-- /wp:separator -->')
            i += 1
            continue

        # Vocabulary Section (## 🎯 今回の語彙 or ## 今回の語彙)
        if '今回の語彙' in stripped or '語彙（重要ボキャブラリー）' in stripped:
            v_title = format_inline_markdown(re.sub(r'^##\s*', '', stripped).strip())
            i += 1
            lead_text = ""
            vocab_items = []
            current_item = None

            while i < len(lines):
                cur = lines[i].strip()
                if not cur:
                    i += 1
                    continue
                if cur.startswith(('## ', '### ', '---', '***', '___', '[oscss_')):
                    break

                # Header: * **...** 【JLPT ...】
                header_m = re.search(r'^\*\s*\*\*(.+?)\*\*\s*【(?:JLPT\s*)?([Nn][1-5])】', cur)
                if header_m:
                    if current_item:
                        vocab_items.append(current_item)
                    current_item = {
                        "word": header_m.group(1).strip(),
                        "jlpt": header_m.group(2).upper(),
                        "meaning": "",
                        "example": ""
                    }
                    i += 1
                    continue

                if current_item:
                    clean = re.sub(r'^\*\s*', '', cur).strip()
                    clean_plain = re.sub(r'<ruby>(.*?)<rt>.*?</rt></ruby>', r'\1', clean)
                    if '意味：' in clean_plain or '意味:' in clean_plain:
                        val = re.sub(r'^.*?意味[：:]\s*', '', clean).strip()
                        current_item['meaning'] = format_inline_markdown(val)
                    elif '例文：' in clean_plain or '例文:' in clean_plain:
                        val = re.sub(r'^.*?例文[：:]\s*', '', clean).strip()
                        current_item['example'] = format_inline_markdown(val)
                    else:
                        if not current_item['meaning']:
                            current_item['meaning'] = format_inline_markdown(clean)
                        elif not current_item['example']:
                            current_item['example'] = format_inline_markdown(clean)
                else:
                    if not lead_text:
                        lead_text = format_inline_markdown(cur)
                    else:
                        lead_text += "<br>" + format_inline_markdown(cur)
                i += 1

            if current_item:
                vocab_items.append(current_item)

            cards_html = []
            for it in vocab_items:
                badge_cls = f"c-badge--jlpt-{it['jlpt'].lower()}"
                card = f"""    <div class="c-vocab-card">
      <div class="c-vocab-card__header">
        <span class="c-vocab-card__word">{it['word']}</span>
        <span class="c-badge c-badge--jlpt {badge_cls}">JLPT {it['jlpt']}</span>
      </div>
      <p class="c-vocab-card__meaning"><strong>意味：</strong>{it['meaning']}</p>
      <p class="c-vocab-card__example"><strong>例文：</strong>{it['example']}</p>
    </div>"""
                cards_html.append(card)

            cards_joined = "\n".join(cards_html)
            lead_html = f'<p class="c-vocab-box__lead">{lead_text}</p>' if lead_text else ''
            box_html = f"""<div class="c-vocab-box">
  <h3 class="c-vocab-box__title">{v_title}</h3>
  {lead_html}
  <div class="c-vocab-grid">
{cards_joined}
  </div>
</div>"""
            blocks.append(f"<!-- wp:html -->\n{box_html}\n<!-- /wp:html -->")
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

        # Image
        img_match = re.match(r'!\[(.*?)\]\((.*?)\)', stripped)
        if img_match:
            alt = img_match.group(1)
            src = img_match.group(2)
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

            balloon_match = re.match(r'^([👔🚗🇯🇵📱👨‍💼👩‍💼])\s*\*\*(.+?)\*\*：(.*)$', qlines[0].strip())
            if balloon_match:
                speaker_icon = balloon_match.group(1)
                speaker_name = balloon_match.group(2)
                dialogue_text = balloon_match.group(3)

                pos = "right" if speaker_icon == "🚗" or "オスカー" in speaker_name else "left"
                avatar_class = "avatar-oscar" if pos == "right" else "avatar-tanaka" if "田中" in speaker_name else "avatar-ren" if "レン" in speaker_name else "avatar-other"
                clean_name = re.sub(r'<ruby>(.*?)<rt>.*?</rt></ruby>', r'\1', speaker_name)

                p_tags = f"<p>{format_inline_markdown(dialogue_text)}</p>"
                for extra in qlines[1:]:
                    if extra.strip():
                        p_tags += f"<p>{format_inline_markdown(extra.strip())}</p>"

                balloon_html = f"""<div class="c-balloon c-balloon--{pos}">
  <div class="c-balloon__avatar {avatar_class}">
    <span class="c-balloon__icon">{speaker_icon}</span>
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

        # Paragraph
        p_lines = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(('#', '>', '---', '***', '___', '* ', '- ', '![')):
            if lines[i].strip().startswith('[oscss_') or lines[i].strip().startswith('<div'):
                break
            p_lines.append(lines[i].strip())
            i += 1

        if p_lines:
            p_text = format_inline_markdown("<br />".join(p_lines))
            blocks.append(f"<!-- wp:paragraph -->\n<p>{p_text}</p>\n<!-- /wp:paragraph -->")

    return "\n\n".join(blocks)

# Execute updates
targets = [
    (2472, "content/posts/2026-10-13-kotoba-no-aya-is-shouchidesu-wrong-business-japanese-trap.md"),
    (2474, "content/posts/2026-10-14-street-japanese-city-hall-resident-registration-dungeon-guide.md"),
    (2476, "content/posts/2026-10-15-japanese-comparing-rashii-souda-youda-differences.md"),
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

for post_id, md_path in targets:
    gutenberg_content = parse_markdown_to_gutenberg(md_path)
    b64_content = base64.b64encode(gutenberg_content.encode('utf-8')).decode('ascii')

    php_code = f"""<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$b64 = '{b64_content}';
$content = base64_decode($b64);

wp_update_post(array(
    'ID' => {post_id},
    'post_content' => $content
));

echo "[RESTORED Post {post_id}] Content length: " . strlen($content) . PHP_EOL;
"""
    with sftp.open('restore_single_post.php', 'w') as f:
        f.write(php_code)

    stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php restore_single_post.php && rm restore_single_post.php')
    print(stdout.read().decode('utf-8', errors='replace'))

# Purge cache
stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php -r "require(getenv(\'HOME\') . \'/web/nihongo.oscarchair.jp/wp-load.php\'); if(has_action(\'litespeed_purge_all\')) { do_action(\'litespeed_purge_all\'); echo \'LiteSpeed Cache Purged All!\'; }"')
print(stdout.read().decode('utf-8', errors='replace'))

sftp.close()
ssh.close()
