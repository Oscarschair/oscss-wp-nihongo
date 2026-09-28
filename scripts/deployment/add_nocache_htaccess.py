# -*- coding: utf-8 -*-
import paramiko

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

sftp = ssh.open_sftp()
with sftp.open('web/nihongo.oscarchair.jp/.htaccess', 'r') as f:
    content = f.read().decode('utf-8')

no_cache_block = """
# Disable HTML browser cache to ensure immediate updates
<IfModule mod_headers.c>
Header set Cache-Control "no-cache, no-store, must-revalidate"
Header set Pragma "no-cache"
Header set Expires "0"
</IfModule>
"""

if 'Disable HTML browser cache' not in content:
    new_content = no_cache_block.strip() + "\n\n" + content
    with sftp.open('web/nihongo.oscarchair.jp/.htaccess', 'w') as f:
        f.write(new_content.encode('utf-8'))
    print("Added no-cache headers to server .htaccess successfully!")
else:
    print("Already present in .htaccess")

sftp.close()
ssh.close()
