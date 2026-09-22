import paramiko, os

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

files = [
    'assets/images/thumbnails/thumb-street-kaitenzushi-rpg.jpg',
    'assets/images/thumbnails/thumb-street-kaitenzushi-rpg.webp',
    'assets/images/thumbnails/thumb-street-ramen-ticket-rpg.jpg',
    'assets/images/thumbnails/thumb-street-ramen-ticket-rpg.webp',
]

for local in files:
    fname = os.path.basename(local)
    remote_theme = f'web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/thumbnails/{fname}'
    remote_upload = f'web/nihongo.oscarchair.jp/wp-content/uploads/2026/09/{fname}'
    
    print(f'Uploading {fname} ({os.path.getsize(local)} bytes)...')
    sftp.put(local, remote_theme)
    sftp.put(local, remote_upload)

sftp.close()

# Purge cache via script file
purge_cmd = "/usr/local/php/8.2/bin/php -r \"require('web/nihongo.oscarchair.jp/wp-load.php'); if(function_exists('opcache_reset')) opcache_reset(); if(class_exists('LiteSpeed\\\\Purge')) \\LiteSpeed\\Purge::purge_all(); wp_cache_flush(); echo 'Cache Purged!';\""
stdin, stdout, stderr = ssh.exec_command(purge_cmd)
print("Purge result:", stdout.read().decode('utf-8', errors='ignore'))
ssh.close()
print("Successfully synced unique equipment thumbnails!")
