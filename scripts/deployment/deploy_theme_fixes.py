import sys
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()
print("Connected to SSH successfully!")

remote_theme_base = "web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/"

# Upload single.php
sftp.put("single.php", remote_theme_base + "single.php")
print("Uploaded single.php")

# Upload functions/filter.php
sftp.put("functions/filter.php", remote_theme_base + "functions/filter.php")
print("Uploaded functions/filter.php")

# Upload main.css
sftp.put("assets/css/main.css", remote_theme_base + "assets/css/main.css")
print("Uploaded assets/css/main.css")

# Upload main.js
sftp.put("assets/js/main.js", remote_theme_base + "assets/js/main.js")
print("Uploaded assets/js/main.js")

sftp.close()

# Purge cache
stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php -r "require(getenv(\'HOME\') . \'/web/nihongo.oscarchair.jp/wp-load.php\'); if(has_action(\'litespeed_purge_all\')) { do_action(\'litespeed_purge_all\'); echo \'LiteSpeed cache purged!\'; }"')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
print("Deployment completed successfully!")
