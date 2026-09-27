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

remote_theme_base = 'web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo'
remote_uploads_base = 'web/nihongo.oscarchair.jp/wp-content/uploads/2026/09'

files = [
    'assets/images/posts/kotoba-shouchidesu-office-confusion.jpg',
    'assets/images/posts/kotoba-shouchidesu-office-confusion.webp'
]

for lf in files:
    rf_theme = f'{remote_theme_base}/{lf}'
    sftp.put(lf, rf_theme)
    print(f'[THEME] Uploaded {rf_theme}')
    
    fname = lf.split('/')[-1]
    rf_upload = f'{remote_uploads_base}/{fname}'
    sftp.put(lf, rf_upload)
    print(f'[UPLOADS] Uploaded {rf_upload}')

sftp.close()

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php -r "require(getenv(\'HOME\') . \'/web/nihongo.oscarchair.jp/wp-load.php\'); if(has_action(\'litespeed_purge_all\')) { do_action(\'litespeed_purge_all\'); echo \'Cache purged.\'; }"')
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
