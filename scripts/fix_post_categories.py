import paramiko

env_data = {}
with open('.env.deploy', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env_data[k.strip()] = v.strip()

host = env_data.get('SSH_HOST', 'ssh.lolipop.jp')
port = int(env_data.get('SSH_PORT', 2222))
user = env_data.get('SSH_USER')
password = env_data.get('SSH_PASS')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=host, port=port, username=user, password=password, look_for_keys=False, allow_agent=False)

sftp = ssh.open_sftp()
with sftp.open('fix_cats.php', 'w') as f:
    f.write("""<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$cat = get_category_by_slug('カルチャーショック');
if (!$cat) {
    // スラッグがURLエンコードされている場合
    $cat = get_category_by_slug(urlencode('カルチャーショック'));
}
if (!$cat) {
    $cat = get_term_by('name', 'カルチャーショック', 'category');
}

echo "Found Culture Shock Cat ID: " . ($cat ? $cat->term_id : 'NONE') . "\\n";

if ($cat) {
    wp_set_post_categories(109, array($cat->term_id));
    wp_set_post_categories(111, array($cat->term_id));
    echo "Set category for posts 109 and 111 successfully!\\n";
}

if (defined('LSCWP_V')) {
    do_action('litespeed_purge_all');
}
if (class_exists('LiteSpeed\\Purge')) {
    LiteSpeed\\Purge::purge_all();
}
if (function_exists('opcache_reset')) {
    opcache_reset();
}
echo "Purged cache!\\n";
""")

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php fix_cats.php')
out = stdout.read().decode('utf-8', errors='ignore')
print(out)

ssh.exec_command('rm fix_cats.php')
sftp.close()
ssh.close()
