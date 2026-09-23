import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import paramiko

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

php_code = """<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$tag = get_term_by('name', 'サバイバル', 'post_tag');
echo "Tag obj:\n";
print_r($tag);

if ($tag) {
    $posts = get_posts(array(
        'tag_id' => $tag->term_id,
        'post_type' => 'any',
        'post_status' => 'any',
        'numberposts' => 10
    ));
    echo "Posts count with get_posts: " . count($posts) . "\\n";
    foreach ($posts as $p) {
        echo "Post ID: {$p->ID}, Status: {$p->post_status}, Date: {$p->post_date}, Title: {$p->post_title}\\n";
    }

    // WP_Query (simulating the tag archive)
    $q = new WP_Query(array(
        'tag_id' => $tag->term_id,
        'post_type' => 'post',
        'post_status' => 'publish'
    ));
    echo "WP_Query published posts: " . $q->found_posts . "\\n";
    
    // Check term relationships table
    global $wpdb;
    $rel = $wpdb->get_results($wpdb->prepare(
        "SELECT tr.*, p.post_title, p.post_status, p.post_date 
         FROM {$wpdb->term_relationships} tr 
         JOIN {$wpdb->term_taxonomy} tt ON tr.term_taxonomy_id = tt.term_taxonomy_id 
         JOIN {$wpdb->posts} p ON tr.object_id = p.ID 
         WHERE tt.term_id = %d",
        $tag->term_id
    ));
    echo "Direct DB relationships count: " . count($rel) . "\\n";
    foreach ($rel as $r) {
        echo "Obj ID: {$r->object_id}, Title: {$r->post_title}, Status: {$r->post_status}, Date: {$r->post_date}\\n";
    }
} else {
    echo "Tag 'サバイバル' not found! Listing all tags:\\n";
    $all_tags = get_terms(array('taxonomy' => 'post_tag', 'hide_empty' => false));
    foreach ($all_tags as $t) {
        echo "Tag: {$t->name} (slug: {$t->slug}, count: {$t->count})\\n";
    }
}
"""

with open('check_tag_tmp.php', 'w', encoding='utf-8') as f:
    f.write(php_code)

sftp.put('check_tag_tmp.php', 'check_tag_tmp.php')
stdin, stdout, stderr = ssh.exec_command('LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php check_tag_tmp.php && rm -f check_tag_tmp.php')
print("STDOUT:\n", stdout.read().decode('utf-8', errors='ignore'))
print("STDERR:\n", stderr.read().decode('utf-8', errors='ignore'))

sftp.close()
ssh.close()
