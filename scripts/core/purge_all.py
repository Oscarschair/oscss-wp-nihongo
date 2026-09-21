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
php_purge = """<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

if (function_exists('opcache_reset')) {
    opcache_reset();
}

$cls = 'LiteSpeed\\Purge';
if (class_exists($cls)) {
    $cls::purge_all();
}
echo "Cache purged successfully!\\n";
"""

with sftp.open('purge_clean.php', 'w') as f:
    f.write(php_purge)

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php purge_clean.php')
out = stdout.read().decode('utf-8', errors='ignore')
err = stderr.read().decode('utf-8', errors='ignore')
print("OUT:\n", out)
if err:
    print("ERR:\n", err)

ssh.exec_command('rm purge_clean.php')
sftp.close()
ssh.close()
