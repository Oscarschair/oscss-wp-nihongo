import paramiko

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

cmd = """
rm -rf ~/web/nihongo.oscarchair.jp/wp-content/themes/twentytwenty*
echo "Unused twentytwenty themes removed."

# Test writing
test_file=~/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/quota_test.txt
echo "Quota check OK" > "$test_file"
cat "$test_file"
rm -f "$test_file"
"""

stdin, stdout, stderr = ssh.exec_command(cmd)
print("STDOUT:\n", stdout.read().decode())
print("STDERR:\n", stderr.read().decode())
