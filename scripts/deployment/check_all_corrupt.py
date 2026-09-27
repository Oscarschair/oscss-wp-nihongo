import sys
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

php_code = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$posts = get_posts(array(
    'post_type' => 'post',
    'post_status' => 'any',
    'numberposts' => -1
));

$corrupted = array();

foreach ($posts as $p) {
    $content = $p->post_content;
    $count = substr_count($content, 'c-vocab-card');
    // Each clean vocab box has at most 3 cards (usually 3)
    if ($count > 3) {
        $corrupted[] = array(
            'id' => $p->ID,
            'slug' => $p->post_name,
            'cards' => $count
        );
    }
}

echo "Found " . count($corrupted) . " posts with corrupted extra cards:\n";
foreach ($corrupted as $c) {
    echo "ID: " . $c['id'] . " | " . $c['slug'] . " | cards: " . $c['cards'] . "\n";
}
"""

sftp = ssh.open_sftp()
with sftp.open('check_all_corrupted.php', 'w') as f:
    f.write(php_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php check_all_corrupted.php && rm check_all_corrupted.php')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
