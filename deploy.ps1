# deploy.ps1
# Automated deploy script for oscss-wp-nihongo to Lolipop via SSH / Paramiko

Write-Host "--- oscss-wp-nihongo Deployment & Cache Purge ---" -ForegroundColor Cyan

if (-Not (Test-Path ".env.deploy")) {
    Write-Host "Error: .env.deploy not found." -ForegroundColor Red
    exit 1
}

$envData = @{}
Get-Content ".env.deploy" | ForEach-Object {
    $line = $_.Trim()
    if ($line -match "^[^#].+=.*$") {
        $parts = $line.Split("=", 2)
        if ($parts.Length -eq 2) {
            $key = $parts[0].Trim(); $val = $parts[1].Trim()
            $envData.$key = $val
        }
    }
}

$u = $envData.SSH_USER
$h = $envData.SSH_HOST
$p = $envData.SSH_PORT
$pass = $envData.SSH_PASS
$d = $envData.DEPLOY_DIR

if (-not ($u -and $h -and $p -and $d)) {
    Write-Host "Error: .env.deploy is missing required SSH configuration." -ForegroundColor Red
    exit 1
}

Write-Host "Connecting to $h ($u) and syncing theme files..." -ForegroundColor Cyan

$pyScript = @"
import sys
import os
import paramiko

host = '$h'
port = $p
user = '$u'
password = '$pass'
deploy_dir = '$d'.replace('~/', '')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(hostname=host, port=port, username=user, password=password, look_for_keys=False, allow_agent=False, timeout=15)
except Exception as e:
    print(f'SSH Connect Error: {e}')
    sys.exit(1)

# 1. リモートのディレクトリ作成
ssh.exec_command(f'mkdir -p {deploy_dir}')

# 2. SFTPでテーマファイルを同期
sftp = ssh.open_sftp()
local_root = os.getcwd()

ignore_dirs = {'.git', '.gemini', 'docs', 'node_modules', '__pycache__'}
ignore_files = {'.env.deploy', 'inspect_remote.py', 'deploy.ps1'}

for root, dirs, files in os.walk(local_root):
    dirs[:] = [d for d in dirs if d not in ignore_dirs]
    rel_path = os.path.relpath(root, local_root).replace('\\\\', '/')
    remote_path = deploy_dir if rel_path == '.' else f'{deploy_dir}/{rel_path}'
    
    try:
        sftp.mkdir(remote_path)
    except:
        pass
        
    for file in files:
        if file in ignore_files or file.endswith('.py') or file.endswith('.log'):
            continue
        local_file = os.path.join(root, file)
        remote_file = f'{remote_path}/{file}'.replace('//', '/')
        print(f'Uploading: {rel_path}/{file}')
        sftp.put(local_file, remote_file)

sftp.close()

# 3. キャッシュパージ
php_inline = \"define('WP_USE_THEMES', false); require('../../../wp-load.php'); if (function_exists('opcache_reset')) { opcache_reset(); } do_action('litespeed_purge_all'); if (class_exists('LiteSpeed\\\\\\\\Purge')) { LiteSpeed\\\\\\\\Purge::purge_all(); } echo 'Cache flushed successfully\\\\n';\"
remote_cmd = f'cd {deploy_dir} && /usr/local/php/8.2/bin/php -r \"{php_inline}\"'

stdin, stdout, stderr = ssh.exec_command(remote_cmd)
out = stdout.read().decode('utf-8', errors='ignore')
err = stderr.read().decode('utf-8', errors='ignore')

print('[REMOTE CACHE PURGE]')
print(out)
if err:
    print('[STDERR]', err)

ssh.close()
"@

$pyScript | python -

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nDeployment completed successfully!" -ForegroundColor Green
} else {
    Write-Host "`nDeployment failed." -ForegroundColor Red
}
