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
with sftp.open('fix_dates.php', 'w') as f:
    f.write("""<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

// サーバーの現在日時
$now = current_time('mysql');
$now_gmt = current_time('mysql', 1);

$post_ids = array(109, 111);
foreach ($post_ids as $id) {
    wp_update_post(array(
        'ID'            => $id,
        'post_date'     => $now,
        'post_date_gmt' => $now_gmt,
        'post_status'   => 'publish',
    ));
    echo "Updated date for Post $id to $now\\n";
}

if (function_exists('opcache_reset')) {
    opcache_reset();
    echo "OPcache reset successfully.\\n";
}
if (defined('LSCWP_V')) {
    do_action('litespeed_purge_all');
    echo "LiteSpeed cache purged.\\n";
}
""")

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php fix_dates.php')
out = stdout.read().decode('utf-8', errors='ignore')
print(out)

ssh.exec_command('rm fix_dates.php')
sftp.close()
ssh.close()
