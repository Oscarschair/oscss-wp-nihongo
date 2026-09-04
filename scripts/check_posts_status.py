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
with sftp.open('check_posts.php', 'w') as f:
    f.write("""<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
$posts = get_posts(array('post_type' => 'post', 'numberposts' => -1, 'post_status' => 'any'));
foreach ($posts as $p) {
    echo $p->ID . ' | ' . $p->post_status . ' | ' . $p->post_date . ' | ' . $p->post_title . "\\n";
}
""")

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php check_posts.php')
out = stdout.read().decode('utf-8', errors='ignore')
err = stderr.read().decode('utf-8', errors='ignore')
print("OUT:\n", out)
if err:
    print("ERR:\n", err)

ssh.exec_command('rm check_posts.php')
sftp.close()
ssh.close()
