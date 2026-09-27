import paramiko
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

php = """<?php
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
    
    // Clean meaning and example prefixes inside c-vocab-card
    $new_content = preg_replace('/(<strong>意味[：:]<\\/strong>)\\s*(?:<ruby>意味<rt>.*?<\\/rt><\\/ruby>|意味)[：:]\\s*/u', '$1', $content);
    $new_content = preg_replace('/(<strong>例文[：:]<\\/strong>)\\s*(?:<ruby>例文<rt>.*?<\\/rt><\\/ruby>|例文)[：:]\\s*/u', '$1', $new_content);
    
    if ($new_content !== $content) {
        wp_update_post(array(
            'ID' => $p->ID,
            'post_content' => $new_content
        ));
        $fixed++;
        echo "[STRIPPED DUP PREFIX] Post ID " . $p->ID . PHP_EOL;
    }
}

echo "Total posts stripped dup prefixes: " . $fixed . PHP_EOL;

if (has_action('litespeed_purge_all')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed Cache Purged All!" . PHP_EOL;
}
"""

sftp = ssh.open_sftp()
with sftp.open('strip_dup_prefixes.php', 'w') as f:
    f.write(php)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php strip_dup_prefixes.php && rm strip_dup_prefixes.php')
out = stdout.read().decode('utf-8', errors='replace')
print(out)
ssh.close()
