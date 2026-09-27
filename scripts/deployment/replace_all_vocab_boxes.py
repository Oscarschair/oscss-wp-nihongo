import glob
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

def parse_vocab_box_from_markdown(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()
        
    match = re.search(r'##\s*🎯?\s*.*?(?:語彙|ボキャブラリー).*?\n(.*?)(?=\n---|\Z)', text, re.DOTALL)
    if not match:
        return None
        
    lines = match.group(1).split('\n')
    lead_text = ""
    vocab_items = []
    current_item = None
    
    for l in lines:
        cur = l.strip()
        if not cur:
            continue
        if cur.startswith(('## ', '### ', '---', '***', '___', '[oscss_')):
            break
            
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
                
    if current_item:
        vocab_items.append(current_item)
        
    if not vocab_items:
        return None
        
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
  <h3 class="c-vocab-box__title">🎯 今回の語彙（重要ボキャブラリー）</h3>
  {lead_html}
  <div class="c-vocab-grid">
{cards_joined}
  </div>
</div>"""
    return box_html

# Build map: slug -> box_html
slug_to_box = {}
for md in glob.glob('content/posts/*.md'):
    box = parse_vocab_box_from_markdown(md)
    if box:
        fname = os.path.basename(md)
        # slug is filename without date prefix and .md
        slug = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', fname).replace('.md', '')
        slug_to_box[slug] = box

print(f"Generated clean vocab boxes for {len(slug_to_box)} markdown files.")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

# Upload json map
with sftp.open('vocab_box_map.json', 'w') as jf:
    jf.write(json.dumps(slug_to_box, ensure_ascii=False))

php_replace = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$json_str = file_get_contents('vocab_box_map.json');
$map = json_decode($json_str, true);

$posts = get_posts(array(
    'post_type' => 'post',
    'post_status' => 'any',
    'numberposts' => -1
));

$updated = 0;

foreach ($posts as $p) {
    $slug = $p->post_name;
    if (isset($map[$slug])) {
        $clean_box = $map[$slug];
        $content = $p->post_content;
        
        // Match existing c-vocab-box (with or without wp:html comments)
        $pattern = '/(?:<!-- wp:html -->\\s*)?<div class="c-vocab-box">.*?<\\/div>(?:\\s*<!-- \\/wp:html -->)?/s';
        
        if (preg_match($pattern, $content)) {
            $new_content = preg_replace($pattern, "<!-- wp:html -->\\n" . $clean_box . "\\n<!-- /wp:html -->", $content);
            if ($new_content !== $content) {
                wp_update_post(array(
                    'ID' => $p->ID,
                    'post_content' => $new_content
                ));
                $updated++;
                echo "[REPLACED VOCAB BOX] Post ID: " . $p->ID . " (" . $slug . ")" . PHP_EOL;
            }
        }
    }
}

echo "Total posts updated with clean vocab boxes: " . $updated . PHP_EOL;

if (has_action('litespeed_purge_all')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache Purged All!" . PHP_EOL;
}
"""

with sftp.open('replace_all_boxes.php', 'w') as pf:
    pf.write(php_replace)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php replace_all_boxes.php && rm replace_all_boxes.php vocab_box_map.json')
out = stdout.read().decode('utf-8', errors='replace')
print(out)
ssh.close()
