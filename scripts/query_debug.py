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
with sftp.open('query_debug.php', 'w') as f:
    f.write("""<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

global $wpdb;
$results = $wpdb->get_results("SELECT ID, post_title, post_status, post_date, post_date_gmt, post_type FROM {$wpdb->posts} WHERE post_type = 'post' ORDER BY post_date DESC");
foreach ($results as $r) {
    echo "ID: {$r->ID} | Status: {$r->post_status} | Date: {$r->post_date} | Date_GMT: {$r->post_date_gmt} | Title: {$r->post_title}\\n";
}
""")

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php query_debug.php')
out = stdout.read().decode('utf-8', errors='ignore')
print(out)

ssh.exec_command('rm query_debug.php')
sftp.close()
ssh.close()
