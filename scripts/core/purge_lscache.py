import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

php = """<?php
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

// LiteSpeed Cache Plugin specific purge
if (defined('LSCWP_V')) {
    apply_filters('litespeed_purge_all', 'All');
    echo "Called filter litespeed_purge_all\\n";
}
if (class_exists('LiteSpeed\\Purge')) {
    \\LiteSpeed\\Purge::purge_all();
    echo "Called LiteSpeed\\\\Purge::purge_all()\\n";
}

// WP Super Cache or other cache plugins if any
if (function_exists('wp_cache_clear_cache')) {
    wp_cache_clear_cache();
}

// Direct file removal of lscache
$upload_dir = wp_upload_dir();
echo "Upload dir: " . $upload_dir['basedir'] . "\\n";

echo "Purge complete.\\n";
"""

with sftp.open('purge_lscache.php', 'w') as f:
    f.write(php)

stdin, stdout, stderr = ssh.exec_command('LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php purge_lscache.php && rm purge_lscache.php')
print(stdout.read().decode('utf-8'))
sftp.close()
ssh.close()
