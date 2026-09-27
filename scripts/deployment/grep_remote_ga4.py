import paramiko

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

stdin, stdout, stderr = ssh.exec_command('grep -rn "G-3QBPY87VPP" web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/')
print('Grep output:\n', stdout.read().decode('utf-8', errors='replace'))

# Check plugins or mu-plugins
stdin, stdout, stderr = ssh.exec_command('grep -rn "G-3QBPY87VPP" web/nihongo.oscarchair.jp/wp-content/plugins/ web/nihongo.oscarchair.jp/wp-content/mu-plugins/')
print('Plugins grep:\n', stdout.read().decode('utf-8', errors='replace'))

ssh.close()
