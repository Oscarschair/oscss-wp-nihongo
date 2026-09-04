import os
import sys
import paramiko

# Load .env.deploy
env_data = {}
if not os.path.exists('.env.deploy'):
    print('Error: .env.deploy not found.')
    sys.exit(1)

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
deploy_dir = env_data.get('DEPLOY_DIR', '~/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/').replace('~/', '')

if not (user and password and deploy_dir):
    print('Error: Missing SSH configuration in .env.deploy')
    sys.exit(1)

print(f'Connecting to {host}:{port} as {user}...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(hostname=host, port=port, username=user, password=password, look_for_keys=False, allow_agent=False, timeout=15)
except Exception as e:
    print(f'SSH Connect Error: {e}')
    sys.exit(1)

# 1. リモートテーマディレクトリの作成
ssh.exec_command(f'mkdir -p {deploy_dir}')

# 2. SFTP同期
sftp = ssh.open_sftp()
local_root = os.getcwd()

ignore_dirs = {'.git', '.gemini', 'docs', 'content', 'node_modules', '__pycache__', 'scripts'}
ignore_files = {'.env', '.env.deploy', '.env.local', 'inspect_remote.py', 'extract_posts.py', 'convert_to_md.py', 'fix_500_error.py', 'deploy.ps1', 'exported_posts.json'}

uploaded_count = 0
for root, dirs, files in os.walk(local_root):
    dirs[:] = [d for d in dirs if d not in ignore_dirs]
    rel_path = os.path.relpath(root, local_root).replace('\\', '/')
    remote_path = deploy_dir.rstrip('/') if rel_path == '.' else f'{deploy_dir.rstrip("/")}/{rel_path}'
    
    try:
        sftp.mkdir(remote_path)
    except:
        pass
        
    for file in files:
        if file in ignore_files or file.endswith('.py') or file.endswith('.log') or file.startswith('.env'):
            continue
        local_file = os.path.join(root, file)
        remote_file = f'{remote_path}/{file}'.replace('//', '/')
        print(f'  -> Uploading: {rel_path}/{file}')
        sftp.put(local_file, remote_file)
        uploaded_count += 1

# 3. キャッシュパージ
php_code = """<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
if (function_exists('opcache_reset')) {
    opcache_reset();
}
do_action('litespeed_purge_all');
if (class_exists('LiteSpeed\\Purge')) {
    LiteSpeed\\Purge::purge_all();
}
echo "Cache flushed successfully\\n";
"""

with sftp.file(f'{deploy_dir.rstrip("/")}/purge_cache_temp.php', 'w') as f:
    f.write(php_code)

sftp.close()

stdin, stdout, stderr = ssh.exec_command(f'/usr/local/php/8.2/bin/php {deploy_dir.rstrip("/")}/purge_cache_temp.php')
out = stdout.read().decode('utf-8', errors='ignore')
err = stderr.read().decode('utf-8', errors='ignore')

print('\n[REMOTE CACHE PURGE]')
print(out.strip())
if err.strip():
    print('[STDERR]', err.strip())

ssh.exec_command(f'rm -f {deploy_dir.rstrip("/")}/purge_cache_temp.php')
ssh.close()

print(f'\nDeployment complete! Total files uploaded: {uploaded_count}')
