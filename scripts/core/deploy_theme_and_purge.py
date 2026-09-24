import os
import glob
import paramiko

env_data = {}
with open('.env.deploy', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env_data[k.strip()] = v.strip()

host = env_data.get('SSH_HOST', 'ssh.lolipop.jp')
port = int(env_data.get('SSH_PORT', 2222))
user = env_data.get('SSH_USER')
password = env_data.get('SSH_PASS')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=host, port=port, username=user, password=password, look_for_keys=False, allow_agent=False)

sftp = ssh.open_sftp()
remote_base = 'web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo'

def sftp_mkdir_p(remote_directory):
    dirs_ = []
    dir_ = remote_directory
    while len(dir_) > 1:
        dirs_.append(dir_)
        dir_, _  = os.path.split(dir_)
    if len(dir_) == 1:
        dirs_.append(dir_)
    while len(dirs_):
        d = dirs_.pop()
        try:
            sftp.stat(d)
        except:
            sftp.mkdir(d)

def upload_file_smart(local_path, target_remote):
    local_mtime = os.path.getmtime(local_path)
    try:
        r_stat = sftp.stat(target_remote)
        # If remote is newer or equal and same size, skip
        if r_stat.st_size == os.path.getsize(local_path) and r_stat.st_mtime >= local_mtime:
            return  # Already up-to-date
    except:
        pass
    for attempt in range(3):
        try:
            sftp.put(local_path, target_remote)
            print(f"Uploaded: {local_path}")
            return
        except Exception as e:
            if attempt == 2:
                raise e
            import time
            time.sleep(1)

# Upload all theme files
theme_files = [
    'functions.php',
    'header.php',
    'footer.php',
    'index.php',
    'front-page.php',
    'single.php',
    'archive.php',
    'page.php',
    'page-articles.php',
    'comments.php',
    'searchform.php',
    '404.php',
    'style.css',
    'screenshot.png',
]

for tf in theme_files:
    if os.path.exists(tf):
        upload_file_smart(tf, f"{remote_base}/{tf}")

# Upload directories
for dir_name in ['functions', 'template-parts', 'assets/css', 'assets/js', 'assets/images']:
    if os.path.exists(dir_name):
        remote_dir = f"{remote_base}/{dir_name}"
        sftp_mkdir_p(remote_dir)
        for root, _, files in os.walk(dir_name):
            for file in files:
                local_path = os.path.join(root, file).replace('\\', '/')
                rel_path = local_path
                target_remote = f"{remote_base}/{rel_path}"
                target_remote_dir = os.path.dirname(target_remote)
                sftp_mkdir_p(target_remote_dir)
                upload_file_smart(local_path, target_remote)

# Purge cache
php_purge = r"""<?php
define('WP_USE_THEMES', false);
require_once(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');

// リライトルールの再フラッシュ
global $wp_rewrite;
$wp_rewrite->set_permalink_structure('/%postname%/');
flush_rewrite_rules(true);

if (function_exists('opcache_reset')) { opcache_reset(); }
if (class_exists('LiteSpeed\\Purge')) { 
    \LiteSpeed\Purge::purge_all(); 
}
do_action('litespeed_purge_all');
wp_cache_flush();

echo "OPcache, LiteSpeed Cache, Object Cache successfully purged & Rewrite rules flushed!\n";
"""



with sftp.open('purge_theme.php', 'w') as f:
    f.write(php_purge)

stdin, stdout, stderr = ssh.exec_command('/usr/local/php/8.2/bin/php purge_theme.php')
out = stdout.read().decode('utf-8', errors='ignore')
err = stderr.read().decode('utf-8', errors='ignore')
print("CACHE PURGE OUT:\n", out)
if err:
    print("CACHE PURGE ERR:\n", err)

ssh.exec_command('rm purge_theme.php')
sftp.close()
ssh.close()
print("Theme deployment finished successfully!")
