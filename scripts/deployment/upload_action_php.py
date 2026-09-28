# -*- coding: utf-8 -*-
import paramiko

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

sftp = ssh.open_sftp()
sftp.put('functions/action.php', 'web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/functions/action.php')
sftp.close()
print("Uploaded functions/action.php successfully!")

# Purge cache
stdin, stdout, stderr = ssh.exec_command("/usr/local/php/8.2/bin/php -r \"define('WP_USE_THEMES', false); require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php'); if(has_action('litespeed_purge_all')){ do_action('litespeed_purge_all'); echo 'LiteSpeed Purged!'; }\"")
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
