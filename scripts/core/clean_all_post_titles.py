import glob
import os
import re
import sys
import base64
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def clean_ruby_from_title(title_str):
    # Strip <rt>...</rt>
    cleaned = re.sub(r'<rt>.*?</rt>', '', title_str, flags=re.DOTALL)
    # Strip <rp>...</rp>
    cleaned = re.sub(r'<rp>.*?</rp>', '', cleaned, flags=re.DOTALL)
    # Strip <ruby> and </ruby>
    cleaned = re.sub(r'</?ruby[^>]*>', '', cleaned)
    # Clean multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

# 1. Clean local markdown files
posts = sorted(glob.glob('content/posts/*.md')) + sorted(glob.glob('content/manga/*.md'))
print(f"Cleaning titles in {len(posts)} markdown files...")

updated_count = 0
for fpath in posts:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    parts = re.split(r'^---\s*$', content, maxsplit=2, flags=re.MULTILINE)
    if len(parts) < 3:
        continue

    fm = parts[1]
    body = parts[2]

    title_m = re.search(r'^(title:\s*["\']?)(.*?)(["\']?\s*)$', fm, flags=re.MULTILINE)
    if title_m:
        raw_t = title_m.group(2)
        cleaned_t = clean_ruby_from_title(raw_t)
        if cleaned_t != raw_t:
            new_fm = fm.replace(title_m.group(0), f'title: "{cleaned_t}"\n', 1)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(f"---{new_fm}---{body}")
            updated_count += 1
            print(f"Cleaned {os.path.basename(fpath)}: {cleaned_t[:45]}")

print(f"Cleaned {updated_count} local markdown titles.\n")

# 2. Update remote WordPress post_title with matching clean local titles
with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

# Build clean title mapping by slug
slug_to_clean_title = {}
for fpath in posts:
    with open(fpath, 'r', encoding='utf-8') as f:
        c = f.read()
    parts = re.split(r'^---\s*$', c, maxsplit=2, flags=re.MULTILINE)
    if len(parts) >= 3:
        fm = parts[1]
        slug_m = re.search(r'^slug:\s*["\']?(.*?)["\']?$', fm, re.MULTILINE)
        title_m = re.search(r'^title:\s*["\']?(.*?)["\']?$', fm, re.MULTILINE)
        if slug_m and title_m:
            slug = slug_m.group(1).strip()
            title = clean_ruby_from_title(title_m.group(1).strip())
            slug_to_clean_title[slug] = title
            # Also register basename without date
            base_slug = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', os.path.splitext(os.path.basename(fpath))[0])
            slug_to_clean_title[base_slug] = title

import json
titles_json = json.dumps(slug_to_clean_title, ensure_ascii=False)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

with sftp.open('clean_titles.json', 'w') as f:
    f.write(titles_json)

php_fix = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$titles = json_decode(file_get_contents('clean_titles.json'), true);
unlink('clean_titles.json');

$posts = get_posts([
    'numberposts' => -1,
    'post_type' => 'post',
    'post_status' => ['publish', 'future', 'draft']
]);

$fixed = 0;
foreach ($posts as $p) {
    $slug = $p->post_name;
    $target_title = null;
    if (isset($titles[$slug])) {
        $target_title = $titles[$slug];
    } else {
        foreach ($titles as $s => $t) {
            if (strpos($s, $slug) === 0 || strpos($slug, $s) === 0) {
                $target_title = $t;
                break;
            }
        }
    }

    if ($target_title && $p->post_title !== $target_title) {
        wp_update_post([
            'ID' => $p->ID,
            'post_title' => $target_title
        ]);
        echo "Fixed WP #{$p->ID} ({$slug}): {$target_title}\n";
        $fixed++;
    }
}

if (has_action('litespeed_purge_all')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache purged.\n";
}
echo "Total fixed WP titles: $fixed\n";
"""

with sftp.open('clean_titles_temp.php', 'w') as f:
    f.write(php_fix)

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php clean_titles_temp.php && rm clean_titles_temp.php')
print(stdout.read().decode('utf-8'))
sftp.close()
ssh.close()

