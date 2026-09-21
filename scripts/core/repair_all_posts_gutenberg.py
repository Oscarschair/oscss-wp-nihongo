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
            code_content = html.escape("\n".join(codelines))
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
                    
                    # Determine avatar and position
                    if any(k in clean_sp for k in ['オスカー', 'あなた', '私', '僕', '客側', '本音']):
                        position = "l"
                        avatar = "https://nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/my-icon.png"
                    else:
                        position = "r"
                        if any(k in clean_sp for k in ['店員', '美容師', '女性', '同僚B']):
                            avatar = "https://nihongo.oscarchair.jp/wp-content/themes/cocoon-master/images/woman.png"
                        else:
                            avatar = "https://nihongo.oscarchair.jp/wp-content/themes/cocoon-master/images/man.png"
                    
                    body_formatted = [format_inline_markdown(bl) for bl in ct_lines if bl]
                    body_html = "<br />".join(body_formatted) if body_formatted else ""
                    
                    blocks.append(f"""<!-- wp:cocoon-blocks/balloon {{"balloonIcon":"{avatar}","balloonName":"{clean_sp}","balloonType":"{position}"}} -->
<div class="speech-wrap sb-id-1 sbs-stn speaker-{position} sb-color-none"><div class="speech-person"><figure class="speech-icon"><img src="{avatar}" alt="{clean_sp}" class="speech-icon-image"/></figure><div class="speech-name">{clean_sp}</div></div><div class="speech-comment"><p>{body_html}</p></div></div>
<!-- /wp:cocoon-blocks/balloon -->""")
            else:
                # Normal quote / information box
                box_lines = [format_inline_markdown(ql) for ql in qlines]
                box_fmt = "<br />".join(box_lines)
                blocks.append(f"<!-- wp:paragraph -->\n<div class=\"information-box\"><p>{box_fmt}</p></div>\n<!-- /wp:paragraph -->")
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
                table_html = "<figure class=\"wp-block-table\"><table><thead><tr>"
                for h in header_cols:
                    table_html += f"<th>{h}</th>"
                table_html += "</tr></thead><tbody>"
                for row in rows:
                    table_html += "<tr>"
                    for cell in row:
                        table_html += f"<td>{cell}</td>"
                    table_html += "</tr>"
                table_html += "</tbody></table></figure>"
                blocks.append(f"<!-- wp:table -->\n{table_html}\n<!-- /wp:table -->")
            continue

        # 6. Shortcode block ([...])
        if line.startswith('[') and line.endswith(']') and not line.startswith('[!'):
            blocks.append(f"<!-- wp:shortcode -->\n{line}\n<!-- /wp:shortcode -->")
            i += 1
            continue

        # 7. Unordered Lists
        if line.startswith('* ') or line.startswith('- '):
            items = []
            while i < len(lines) and (lines[i].strip().startswith('* ') or lines[i].strip().startswith('- ')):
                it_text = format_inline_markdown(lines[i].strip()[2:])
                items.append(it_text)
                i += 1
            blocks.append("<!-- wp:list -->\n<ul>" + "".join([f"<li>{it}</li>" for it in items]) + "</ul>\n<!-- /wp:list -->")
            continue

        # 8. Ordered Lists
        if re.match(r'^\d+\.\s+', line):
            items = []
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i].strip()):
                it_text = format_inline_markdown(re.sub(r'^\d+\.\s+', '', lines[i].strip()))
                items.append(it_text)
                i += 1
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
        title_match = re.search(r'title:\s*["\']?([^"\']+)["\']?', fm)
        desc_match = re.search(r'description:\s*["\']?([^"\']+)["\']?', fm)
        date_match = re.search(r'date:\s*["\']?([^"\']+)["\']?', fm)
        thumb_match = re.search(r'thumbnail:\s*["\']?([^"\']+)["\']?', fm)

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
            html_body = md_to_gutenberg(c)
            updates.append({
                "slug": slug,
                "title": title,
                "desc": desc,
                "date": date_val,
                "cats": cats,
                "tags": tags,
                "thumb_path": thumb_path,
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

with sftp.open('gutenberg_updates.json', 'w') as f:
    f.write(json.dumps(updates, ensure_ascii=False))

php_script = r'''<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/image.php');

$data = json_decode(file_get_contents('gutenberg_updates.json'), true);

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
    if (!empty($item['cats'])) {
        foreach ($item['cats'] as $cslug) {
            $cat_obj = get_category_by_slug($cslug);
            if ($cat_obj) {
                $cat_ids[] = $cat_obj->term_id;
            }
        }
    }

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
        wp_update_post($post_arr);

        if ($thumb_id > 0) {
            set_post_thumbnail($p->ID, $thumb_id);
        }
        echo "Successfully repaired post ID: {$p->ID} (slug: {$slug})\n";
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
            update_post_meta($new_id, '_oscss_post_views', 0);
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

with sftp.open('repair_gutenberg.php', 'w') as f:
    f.write(php_script)

stdin, stdout, stderr = ssh.exec_command('LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php repair_gutenberg.php && rm repair_gutenberg.php gutenberg_updates.json')
out = stdout.read().decode('utf-8', errors='ignore')
err = stderr.read().decode('utf-8', errors='ignore')
print("OUTPUT:\n", out)
if err:
    print("ERR:\n", err)

sftp.close()
ssh.close()
print("Post repair and cache purge completed.")
