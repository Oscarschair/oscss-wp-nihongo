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

remote_php = """<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
$posts = get_posts(array('post_type' => 'post', 'numberposts' => -1, 'post_status' => 'publish'));
foreach ($posts as $p) {
    echo "========================================\n";
    echo "ID: " . $p->ID . " | Title: " . $p->post_title . "\n";
    echo "========================================\n";
    echo $p->post_content . "\n\n";
}
"""

sftp = ssh.open_sftp()
with sftp.open('inspect_tmp.php', 'w') as f:
    f.write(remote_php)

# ロリポップのphpパス /usr/local/php/8.2/bin/php または /usr/local/php/8.1/bin/php /usr/local/php/8.0/bin/php
stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php inspect_tmp.php')
out = stdout.read().decode('utf-8')
err = stderr.read().decode('utf-8')
if not out and err:
    stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.1/bin/php inspect_tmp.php')
    out = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')

print(out)
if err:
    print("ERR:", err)

ssh.exec_command('rm inspect_tmp.php')
sftp.close()
ssh.close()
