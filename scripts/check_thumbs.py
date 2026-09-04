import os
import paramiko

env_data = {}
with open('.env.deploy', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env_data[k.strip()] = v.strip()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=env_data.get('SSH_HOST'), port=int(env_data.get('SSH_PORT')), username=env_data.get('SSH_USER'), password=env_data.get('SSH_PASS'), look_for_keys=False, allow_agent=False)

php = """
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
foreach ([1, 36, 30, 19, 85, 44] as $pid) {
    $tid = get_post_thumbnail_id($pid);
    $url = wp_get_attachment_url($tid);
    $meta = get_post_meta($pid, '_thumbnail_id', true);
    echo "Post {$pid}: tid={$tid} (meta={$meta}) url={$url}\\n";
}
"""

deploy_dir = env_data.get('DEPLOY_DIR', '~/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/').replace('~/', '')
sftp = ssh.open_sftp()
with sftp.file(f'{deploy_dir.rstrip("/")}/check_t.php', 'w') as f:
    f.write("<?php " + php)
sftp.close()

stdin, stdout, stderr = ssh.exec_command(f"/usr/local/php/8.2/bin/php {deploy_dir.rstrip('/')}/check_t.php")
print(stdout.read().decode())
print(stderr.read().decode())
ssh.exec_command(f"rm -f {deploy_dir.rstrip('/')}/check_t.php")
ssh.close()
