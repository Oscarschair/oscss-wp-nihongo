import paramiko

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

cmd = """
echo "=== Nihongo WP-Content ==="
du -sh ~/web/nihongo.oscarchair.jp/wp-content/* 2>/dev/null

echo "=== Top 10 Largest files in Home ==="
find ~ -type f -size +10M -exec ls -lh {} + 2>/dev/null | sort -k 5 -rh | head -n 15

echo "=== LiteSpeed / Cache dirs ==="
du -sh ~/web/nihongo.oscarchair.jp/wp-content/cache 2>/dev/null
du -sh ~/web/nihongo.oscarchair.jp/wp-content/litespeed* 2>/dev/null
"""

stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode())
