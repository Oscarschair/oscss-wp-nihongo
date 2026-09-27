import paramiko
import sys
import base64

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

php_clean = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$posts = get_posts(array(
    'post_type' => 'post',
    'post_status' => 'any',
    'numberposts' => -1
));

$fixed = 0;
foreach ($posts as $p) {
    $content = $p->post_content;
    
    // Check if broken 'n' or duplicate '意味：' in c-vocab-box
    if (strpos($content, '<!-- wp:html -->n<div class="c-vocab-box">') !== false || strpos($content, '>n<') !== false || strpos($content, '意味：意味：') !== false) {
        // Fix newlines: replace '>n<' with '>\\n<'
        // Fix '-->n<' with '-->\\n<'
        // Fix '>n  <' with '>\\n  <'
        $clean = preg_replace('/(?<=>)n(?=\\s*<)/', "\\n", $content);
        $clean = str_replace('<!-- wp:html -->n<div', "<!-- wp:html -->\\n<div", $clean);
        $clean = str_replace('</div>n<!-- /wp:html -->', "</div>\\n<!-- /wp:html -->", $clean);
        $clean = str_replace('意味：意味：', '意味：', $clean);
        $clean = str_replace('例文：例文：', '例文：', $clean);
        $clean = str_replace('<ruby>意味<rt>いみ</rt></ruby>：', '', $clean);
        $clean = str_replace('<ruby>例文<rt>れいぶん</rt></ruby>：', '', $clean);
        
        wp_update_post(array(
            'ID' => $p->ID,
            'post_content' => $clean
        ));
        $fixed++;
        echo "[FIXED VOCAB] Post ID " . $p->ID . PHP_EOL;
    }
}

echo "Total posts cleaned: " . $fixed . PHP_EOL;

if (has_action('litespeed_purge_all')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache Purged All!" . PHP_EOL;
}
"""

sftp = ssh.open_sftp()
with sftp.open('clean_vocab_n.php', 'w') as f:
    f.write(php_clean)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php clean_vocab_n.php && rm clean_vocab_n.php')
out = stdout.read().decode('utf-8', errors='replace')
print(out)

ssh.close()
