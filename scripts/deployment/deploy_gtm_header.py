import paramiko
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

sftp = ssh.open_sftp()
remote_path = 'web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/header.php'
sftp.put('header.php', remote_path)
print(f"Uploaded header.php to {remote_path}")
sftp.close()

# Purge LiteSpeed Cache
stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php -r "require(getenv(\'HOME\') . \'/web/nihongo.oscarchair.jp/wp-load.php\'); if (has_action(\'litespeed_purge_all\')) { do_action(\'litespeed_purge_all\'); echo \'LiteSpeed Cache Purged All!\'; }"')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
