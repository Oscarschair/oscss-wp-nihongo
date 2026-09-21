import paramiko
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

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

files_to_check = [
    'single.php',
    'template-parts/related-posts.php',
    'functions/shortcode.php',
]

print("=== 🔍 PHP構文検証スタート ===")
all_ok = True

for rel_path in files_to_check:
    with open(rel_path, 'rb') as f:
        content = f.read()
    
    safe_name = rel_path.replace('/', '_').replace('\\', '_')
    remote_tmp = f"tmp_check_{safe_name}"
    with sftp.open(remote_tmp, 'wb') as f:
        f.write(content)
        
    cmd = f"/usr/local/php/8.2/bin/php -l {remote_tmp} && rm {remote_tmp}"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    
    if "No syntax errors detected" in out:
        print(f"✅ {rel_path}: {out}")
    else:
        print(f"❌ {rel_path}: ERROR\n{out}\n{err}")
        all_ok = False

sftp.close()
ssh.close()

if all_ok:
    print("\n🎉 すべてのPHPファイルで構文エラーは検出されませんでした！")
else:
    print("\n⚠️ 構文エラーが検出されました。修正が必要です。")
    sys.exit(1)
