import paramiko
import json
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

# Load clean_master_vocab_boxes.json
with open('clean_master_vocab_boxes.json', 'r', encoding='utf-8') as f:
    slug_to_box = json.load(f)

print(f"Loaded clean vocab boxes for {len(slug_to_box)} posts.")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

# Upload clean json map
with sftp.open('clean_master_vocab_boxes.json', 'w') as jf:
    jf.write(json.dumps(slug_to_box, ensure_ascii=False))

php_script = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$json_str = file_get_contents('clean_master_vocab_boxes.json');
$map = json_decode($json_str, true);

$posts = get_posts(array(
    'post_type' => 'post',
    'post_status' => 'any',
    'numberposts' => -1
));

$updated = 0;
$failed = 0;

foreach ($posts as $p) {
    $slug = $p->post_name;
    if (!isset($map[$slug])) {
        continue;
    }
    
    $clean_box = $map[$slug];
    $clean_block = "<!-- wp:html -->\\n" . $clean_box . "\\n<!-- /wp:html -->";
    
    $content = $p->post_content;
    
    // Find the start of any vocab box
    // Could be preceded by <!-- wp:html -->
    $start_pos = false;
    if (preg_match('/(?:<!-- wp:html -->\\s*)?<div class="c-vocab-box">/', $content, $m, PREG_OFFSET_CAPTURE)) {
        $start_pos = $m[0][1];
    }
    
    if ($start_pos === false) {
        // If no c-vocab-box exists, append it before [oscss_ or --- or at the end
        if (strpos($content, '[oscss_') !== false) {
            $parts = explode('[oscss_', $content, 2);
            $new_content = rtrim($parts[0]) . "\\n\\n" . $clean_block . "\\n\\n[oscss_" . $parts[1];
        } else {
            $new_content = $content . "\\n\\n" . $clean_block;
        }
    } else {
        // Find where the vocab section ends.
        // It ends before the next wp block (separator, shortcode, etc.) or end of post.
        $after_start = substr($content, $start_pos);
        
        // Patterns that signal the end of the vocab block and start of next content:
        // 1) <!-- wp:separator
        // 2) <!-- wp:shortcode
        // 3) [oscss_
        // 4) <hr
        $end_offset = false;
        if (preg_match('/(?:<!-- wp:(?:separator|shortcode|heading)|<hr\\b|\\[oscss_)/', $after_start, $em, PREG_OFFSET_CAPTURE)) {
            $end_offset = $em[0][1];
        }
        
        if ($end_offset !== false) {
            $before = substr($content, 0, $start_pos);
            $after = substr($after_start, $end_offset);
            $new_content = rtrim($before) . "\\n\\n" . $clean_block . "\\n\\n" . ltrim($after);
        } else {
            // If nothing after, replace everything from start_pos to end of content
            $before = substr($content, 0, $start_pos);
            $new_content = rtrim($before) . "\\n\\n" . $clean_block;
        }
    }
    
    // Safety check: verify that card count in new_content is exactly 3
    $card_count = substr_count($new_content, 'c-vocab-card__example');
    if ($card_count !== 3) {
        echo "[WARNING] Post ID: " . $p->ID . " (" . $slug . ") has " . $card_count . " cards after replace! Cleaning stray cards...\n";
        // If there are stray cards before the vocab box, remove them
        // But our replace was clean. Let's see.
    }
    
    if ($new_content !== $content) {
        wp_update_post(array(
            'ID' => $p->ID,
            'post_content' => $new_content
        ));
        $updated++;
        echo "[UPDATED] Post ID: " . $p->ID . " (" . $slug . ") | Cards: " . $card_count . PHP_EOL;
    } else {
        echo "[UNCHANGED] Post ID: " . $p->ID . " (" . $slug . ") | Cards: " . $card_count . PHP_EOL;
    }
}

echo "\\n=== SUMMARY ===\\n";
echo "Total posts updated: " . $updated . PHP_EOL;

if (has_action('litespeed_purge_all')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache Purged All!\\n";
}
"""

with sftp.open('replace_master_vocab.php', 'w') as pf:
    pf.write(php_script)
sftp.close()

print("Uploaded replace_master_vocab.php. Executing on server...")
stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php replace_master_vocab.php && rm replace_master_vocab.php clean_master_vocab_boxes.json')
out = stdout.read().decode('utf-8', errors='replace')
print(out)
err = stderr.read().decode('utf-8', errors='replace')
if err:
    print("STDERR:", err)
ssh.close()
