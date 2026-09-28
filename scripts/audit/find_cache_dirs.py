# -*- coding: utf-8 -*-
import paramiko

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

stdin, stdout, stderr = ssh.exec_command('find ~/web/nihongo.oscarchair.jp/wp-content/ -maxdepth 3 -type d -name "*cache*"')
print("Cache dirs:", stdout.read().decode('utf-8', errors='replace'))

# Check lscache in home directory
stdin, stdout, stderr = ssh.exec_command('find ~ -maxdepth 2 -name "*lscache*"')
print("lscache dirs:", stdout.read().decode('utf-8', errors='replace'))
ssh.close()
