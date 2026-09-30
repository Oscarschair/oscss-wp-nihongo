import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

env_data = {}
with open('.env.deploy', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env_data[k.strip()] = v.strip()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    hostname=env_data['SSH_HOST'],
    port=int(env_data['SSH_PORT']),
    username=env_data['SSH_USER'],
    password=env_data['SSH_PASS'],
    look_for_keys=False,
    allow_agent=False
)
sftp = ssh.open_sftp()

php_code = """<?php
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

$test_ids = array(217, 187, 1, 127, 19, 111, 36, 109, 144, 85, 184, 44);

foreach ($test_ids as $id) {
    $p = get_post($id);
    if ($p) {
        $raw = $p->post_title;
        $filtered = get_the_title($id);
        $clean = oscss_get_clean_title($id);
        echo "ID $id:\n";
        echo "  raw     : " . var_export($raw, true) . "\n";
        echo "  filtered: " . var_export($filtered, true) . "\n";
        echo "  clean   : " . var_export($clean, true) . "\n";
    }
}
"""

remote_php = 'web/nihongo.oscarchair.jp/temp_inspect_titles.php'
with sftp.file(remote_php, 'w') as f:
    f.write(php_code)

stdin, stdout, stderr = ssh.exec_command(f'LANG=ja_JP.UTF-8 /usr/local/php/8.2/bin/php $HOME/{remote_php} && rm -f $HOME/{remote_php}')
print(stdout.read().decode('utf-8', errors='ignore'))
sftp.close()
ssh.close()
