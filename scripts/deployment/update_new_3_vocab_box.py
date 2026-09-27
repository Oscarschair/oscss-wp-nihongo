import os
import re
import sys
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

def parse_vocab_from_markdown(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Find vocab section
    match = re.search(r'##\s*🎯?\s*.*?(?:語彙|ボキャブラリー).*?\n(.*?)(?=\n---|\Z)', text, re.DOTALL)
    if not match:
        return None

    section_body = match.group(1).strip()
    lines = [l.strip() for l in section_body.split('\n') if l.strip()]

    lead_text = ""
    items = []
    current_item = None

    for l in lines:
        # Check for item header: * **...** 【JLPT ...】
        header_m = re.search(r'^\*\s*\*\*(.+?)\*\*\s*【(?:JLPT\s*)?([Nn][1-5])】', l)
        if header_m:
            if current_item:
                items.append(current_item)
            current_item = {
                "word": header_m.group(1).strip(),
                "jlpt": header_m.group(2).upper(),
                "meaning": "",
                "example": ""
            }
            continue

        if current_item:
            # Check meaning / example
            clean = re.sub(r'^\*\s*', '', l).strip()
            # remove ruby from "意味" or "例文" to match easily
            clean_plain = re.sub(r'<ruby>(.*?)<rt>.*?</rt></ruby>', r'\1', clean)
            if '意味：' in clean_plain or '意味:' in clean_plain:
                current_item['meaning'] = re.sub(r'^.*?意味[：:]\s*', '', clean).strip()
            elif '例文：' in clean_plain or '例文:' in clean_plain:
                current_item['example'] = re.sub(r'^.*?例文[：:]\s*', '', clean).strip()
            else:
                if not current_item['meaning']:
                    current_item['meaning'] = clean
                elif not current_item['example']:
                    current_item['example'] = clean
        else:
            if not lead_text:
                lead_text = l
            else:
                lead_text += "<br>" + l

    if current_item:
        items.append(current_item)

    if not items:
        return None

    # Build HTML
    cards_html = []
    for it in items:
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
    lead_p = f'<p class="c-vocab-box__lead">{lead_text}</p>' if lead_text else ''
    box_html = f"""<!-- wp:html -->
<div class="c-vocab-box">
  <h3 class="c-vocab-box__title">🎯 今回の語彙（重要ボキャブラリー）</h3>
  {lead_p}
  <div class="c-vocab-grid">
{cards_joined}
  </div>
</div>
<!-- /wp:html -->"""
    return box_html

# Target posts
targets = [
    (2472, "content/posts/2026-10-13-kotoba-no-aya-is-shouchidesu-wrong-business-japanese-trap.md"),
    (2474, "content/posts/2026-10-14-street-japanese-city-hall-resident-registration-dungeon-guide.md"),
    (2476, "content/posts/2026-10-15-japanese-comparing-rashii-souda-youda-differences.md"),
]

for post_id, md_path in targets:
    box = parse_vocab_from_markdown(md_path)
    if not box:
        print(f"[ERROR] Could not parse vocab for {post_id}")
        continue

    # Execute PHP to replace raw list with c-vocab-box
    php_code = f"""<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$p = get_post({post_id});
if ($p) {{
    $content = $p->post_content;
    
    // Check if raw vocab heading exists
    // Replace heading + list up to series/related or hr
    $pattern = '/<!-- wp:heading.*?-->\\s*<h2[^>]*>.*?語彙.*?<\\/h2>\\s*<!-- \\/wp:heading -->.*?(?=<!-- wp:separator|<!-- wp:paragraph -->\\s*<p>\\[oscss_series|\\Z)/s';
    
    $box_html = {repr(box)};
    
    if (preg_match($pattern, $content)) {{
        $new_content = preg_replace($pattern, $box_html . "\\n\\n", $content);
        wp_update_post(array(
            'ID' => {post_id},
            'post_content' => $new_content
        ));
        echo "[UPDATED Post {post_id}] Successfully replaced with c-vocab-box!" . PHP_EOL;
    }} else {{
        echo "[WARNING Post {post_id}] Pattern not matched, checking c-vocab-box..." . PHP_EOL;
    }}
}}
"""
    sftp = ssh.open_sftp()
    with sftp.open('update_post_vocab.php', 'w') as f:
        f.write(php_code)
    sftp.close()

    stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php update_post_vocab.php && rm update_post_vocab.php')
    print(stdout.read().decode('utf-8', errors='replace'))

# Purge cache
stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php -r "require(getenv(\'HOME\') . \'/web/nihongo.oscarchair.jp/wp-load.php\'); if(has_action(\'litespeed_purge_all\')) do_action(\'litespeed_purge_all\'); echo \'Cache purged.\';"')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
