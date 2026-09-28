import paramiko
import json
import sys
import re

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

with open('clean_master_vocab_boxes.json', 'r', encoding='utf-8') as f:
    slug_to_box = json.load(f)

print(f"Loaded {len(slug_to_box)} clean vocab boxes.")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

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

foreach ($posts as $p) {
    $slug = $p->post_name;
    if (!isset($map[$slug])) {
        continue;
    }
    
    $clean_box = $map[$slug];
    $clean_block = "<!-- wp:html -->\\n" . $clean_box . "\\n<!-- /wp:html -->";
    
    $content = $p->post_content;
    
    // Check if post already has exact clean_box
    if (strpos($content, $clean_box) !== false) {
        echo "[ALREADY OK] Post ID: " . $p->ID . " (" . $slug . ")" . PHP_EOL;
        continue;
    }
    
    $start_pos = false;
    $is_plain = false;
    $lead_len = 0;
    
    // 1. Detect existing c-vocab-box
    if (preg_match('/(?:<!-- wp:html -->\\s*)?<div class="c-vocab-box">/', $content, $m, PREG_OFFSET_CAPTURE)) {
        $start_pos = $m[0][1];
    }
    // 2. Or detect plain heading (H2 or H3 with 語彙 or ボキャブラリー)
    elseif (preg_match('/(?:<!-- wp:heading.*?-->\\s*)?<h[23][^>]*>.*?🎯?.*?(?:語彙|ボキャブラリー).*?<\\/h[23]>(?:\\s*<!-- \\/wp:heading -->)?/u', $content, $m, PREG_OFFSET_CAPTURE)) {
        $start_pos = $m[0][1];
        $is_plain = true;
        $lead_len = strlen($m[0][0]);
    }
    
    if ($start_pos !== false) {
        $after_start = substr($content, $start_pos);
        $search_after = $is_plain ? substr($after_start, $lead_len) : $after_start;
        
        // Find next section boundary
        if (preg_match('/(?:<!-- wp:(?:separator|shortcode|heading)|<hr\\b|\\[oscss_)/u', $search_after, $em, PREG_OFFSET_CAPTURE)) {
            $end_offset = ($is_plain ? $lead_len : 0) + $em[0][1];
            $before = substr($content, 0, $start_pos);
            $after = substr($after_start, $end_offset);
            $new_content = rtrim($before) . "\\n\\n" . $clean_block . "\\n\\n" . ltrim($after);
        } else {
            $before = substr($content, 0, $start_pos);
            $new_content = rtrim($before) . "\\n\\n" . $clean_block;
        }
    } else {
        // Append before shortcode or at end
        if (strpos($content, '[oscss_') !== false) {
            $parts = explode('[oscss_', $content, 2);
            $new_content = rtrim($parts[0]) . "\\n\\n" . $clean_block . "\\n\\n[oscss_" . $parts[1];
        } else {
            $new_content = $content . "\\n\\n" . $clean_block;
        }
    }
    
    if ($new_content !== $content) {
        wp_update_post(array(
            'ID' => $p->ID,
            'post_content' => $new_content
        ));
        $updated++;
        echo "[RESTORED VOCAB BOX] Post ID: " . $p->ID . " (" . $slug . ")" . PHP_EOL;
    }
}

echo "\\nTotal posts restored with clean vocab card box: " . $updated . PHP_EOL;

if (has_action('litespeed_purge_all')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache Purged All!\\n";
}
"""

with sftp.open('restore_vocab_all.php', 'w') as pf:
    pf.write(php_script)
sftp.close()

print("Executing restore_vocab_all.php...")
stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php restore_vocab_all.php && rm restore_vocab_all.php clean_master_vocab_boxes.json')
out = stdout.read().decode('utf-8', errors='replace')
print(out)
err = stderr.read().decode('utf-8', errors='replace')
if err:
    print("STDERR:", err)
ssh.close()
