import os
import sys
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Load env
with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    hostname=env['SSH_HOST'],
    port=int(env['SSH_PORT']),
    username=env['SSH_USER'],
    password=env['SSH_PASS'],
    look_for_keys=False,
    allow_agent=False,
    timeout=30
)

php_script = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
require_once(ABSPATH . 'wp-admin/includes/taxonomy.php');

echo "=== CURRENT CATEGORIES ===\\n";
$terms = get_terms([
    'taxonomy' => 'category',
    'hide_empty' => false,
]);
foreach ($terms as $t) {
    echo "ID: {$t->term_id} | Name: {$t->name} | Slug: {$t->slug} | Count: {$t->count}\\n";
}

echo "\\n=== POSTS WITH UNCATEGORIZED OR UNEXPECTED CATEGORIES ===\\n";
$posts = get_posts([
    'post_type' => 'post',
    'post_status' => ['publish', 'future', 'draft'],
    'numberposts' => -1,
]);

$fixed_count = 0;
foreach ($posts as $p) {
    $cats = wp_get_post_categories($p->ID);
    $cat_objs = array_map('get_category', $cats);
    $cat_names = array_map(function($c) { return $c->name; }, $cat_objs);
    $cat_slugs = array_map(function($c) { return $c->slug; }, $cat_objs);
    
    $is_problematic = in_array('uncategorized', $cat_slugs) || in_array('日本語比べ', $cat_names) || in_array('言葉のあや', $cat_names) || empty($cats);
    
    if ($is_problematic) {
        echo "Post ID: {$p->ID} [{$p->post_date}] Slug: {$p->post_name}\\n";
        echo "  Current Cats: " . implode(', ', $cat_names) . "\\n";
        
        // Determine correct category from post_name (slug) or title
        $target_slug = '';
        if (strpos($p->post_name, 'street-japanese') !== false || strpos($p->post_title, '街角サバイバル') !== false) {
            $target_slug = 'street-japanese';
        } elseif (strpos($p->post_name, 'comparing') !== false || strpos($p->post_title, 'くらべてみました') !== false) {
            $target_slug = 'comparing';
        } elseif (strpos($p->post_name, 'kotoba-no-aya') !== false || strpos($p->post_title, 'ことばのあや') !== false) {
            $target_slug = 'kotoba-no-aya';
        } elseif (strpos($p->post_name, 'culture-shock') !== false || strpos($p->post_title, 'カルチャーショック') !== false) {
            $target_slug = 'culture-shock';
        }
        
        if ($target_slug) {
            $cat_term = get_category_by_slug($target_slug);
            if ($cat_term) {
                wp_set_post_categories($p->ID, [$cat_term->term_id]);
                echo "  -> FIXED to: {$cat_term->name} (ID: {$cat_term->term_id})\\n";
                $fixed_count++;
            } else {
                echo "  -> ERROR: Target term for slug '{$target_slug}' not found!\\n";
            }
        } else {
            echo "  -> WARNING: Could not determine category!\\n";
        }
    }
}
echo "\\nTotal posts fixed: {$fixed_count}\\n";

// Delete unwanted empty categories: '日本語比べ', '言葉のあや'
echo "\\n=== CLEANING UNWANTED CATEGORIES ===\\n";
$unwanted = ['日本語比べ', '言葉のあや'];
foreach ($unwanted as $u_name) {
    $t = get_term_by('name', $u_name, 'category');
    if ($t) {
        $res = wp_delete_term($t->term_id, 'category');
        if (!is_wp_error($res) && $res) {
            echo "Deleted term: {$u_name} (ID: {$t->term_id})\\n";
        } else {
            echo "Could not delete term: {$u_name}\\n";
        }
    }
}

// Clear LiteSpeed Cache if available
if (defined('LSCWP_V')) {
    do_action('litespeed_purge_all');
    echo "\\nLiteSpeed Cache Purged!\\n";
} elseif (class_exists('LiteSpeed_Cache_API')) {
    LiteSpeed_Cache_API::purge_all();
    echo "\\nLiteSpeed Cache Purged via API!\\n";
}
"""

remote_path = "fix_categories.php"
sftp = ssh.open_sftp()
with sftp.file(remote_path, 'w') as f:
    f.write(php_script)
sftp.close()

stdin, stdout, stderr = ssh.exec_command(f"/usr/local/php/8.2/bin/php {remote_path}")
out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')

print(out)
if err:
    print("[STDERR]", err)

# Remove script from remote
ssh.exec_command(f"rm {remote_path}")
ssh.close()
