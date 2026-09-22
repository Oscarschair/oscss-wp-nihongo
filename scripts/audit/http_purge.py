import paramiko
import urllib.request

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
with open('.env.deploy', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))
ssh.connect(hostname=env['SSH_HOST'], port=int(env['SSH_PORT']), username=env['SSH_USER'], password=env['SSH_PASS'], look_for_keys=False, allow_agent=False)

# Put a web-accessible purge trigger that sends LiteSpeed purge headers
purge_script = """<?php
define('WP_USE_THEMES', false);
require_once(__DIR__ . '/wp-load.php');

if (function_exists('opcache_reset')) {
    opcache_reset();
}

// Send LiteSpeed Web Server Purge Header
header('X-LiteSpeed-Purge: *');
header('X-LiteSpeed-Purge: public:*');

if (class_exists('LiteSpeed\\Purge')) {
    \\LiteSpeed\\Purge::purge_all();
}
do_action('litespeed_purge_all');
wp_cache_flush();

echo "HTTP_PURGE_SUCCESS";
"""

sftp = ssh.open_sftp()
with sftp.open('web/nihongo.oscarchair.jp/purge_trigger.php', 'w') as f:
    f.write(purge_script)
sftp.close()

# Call via HTTP
try:
    req = urllib.request.Request("https://nihongo.oscarchair.jp/purge_trigger.php", headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        print("HTTP Purge Response:", resp.read().decode('utf-8'))
except Exception as e:
    print("HTTP Purge Error:", e)

# Delete trigger script
ssh.exec_command('rm web/nihongo.oscarchair.jp/purge_trigger.php')
ssh.close()
