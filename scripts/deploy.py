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

deploy_dir = env_data.get('DEPLOY_DIR', '~/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/').replace('~/', '')
sftp = ssh.open_sftp()

files_to_upload = [
    ('assets/css/main.css', 'assets/css/main.css'),
    ('functions.php', 'functions.php'),
    ('footer.php', 'footer.php'),
    ('front-page.php', 'front-page.php'),
]

for local_path, remote_path in files_to_upload:
    sftp.put(local_path, f"{deploy_dir.rstrip('/')}/{remote_path}")
    print(f"Uploaded {local_path}")

php_purge = """<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
if (function_exists('opcache_reset')) { opcache_reset(); }
if (class_exists('LiteSpeed\\Purge')) { LiteSpeed\\Purge::purge_all(); }
echo "Cache purged\\n";
"""
purge_path = f"{deploy_dir.rstrip('/')}/purge.php"
with sftp.file(purge_path, "w") as f:
    f.write(php_purge)
sftp.close()

stdin, stdout, stderr = ssh.exec_command(f"/usr/local/php/8.2/bin/php {purge_path}")
print(stdout.read().decode())
ssh.exec_command(f"rm -f {purge_path}")
ssh.close()
print("Deployment and cache purge complete!")
