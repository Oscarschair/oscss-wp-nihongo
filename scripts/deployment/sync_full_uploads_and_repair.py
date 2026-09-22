import paramiko, sys

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

# 1. uploads配下のすべての年月ディレクトリへ最新画像をコピー
shell_cmd = """
THEME_DIR=~/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo
UPLOADS_DIR=~/web/nihongo.oscarchair.jp/wp-content/uploads

echo "=== Copying all theme thumbnails & post images to uploads directories ==="

# Copy thumbnails
find "$THEME_DIR/assets/images/thumbnails" -type f | while read f; do
  fname=$(basename "$f")
  # find existing occurrences in uploads
  find "$UPLOADS_DIR" -type f -name "$fname" | while read dest; do
    cp -f "$f" "$dest"
    echo "Overwritten: $dest"
  done
  # also ensure in 2026/09
  mkdir -p "$UPLOADS_DIR/2026/09"
  cp -f "$f" "$UPLOADS_DIR/2026/09/$fname"
done

# Copy posts images
find "$THEME_DIR/assets/images/posts" -type f | while read f; do
  fname=$(basename "$f")
  find "$UPLOADS_DIR" -type f -name "$fname" | while read dest; do
    cp -f "$f" "$dest"
    echo "Overwritten: $dest"
  done
  mkdir -p "$UPLOADS_DIR/2026/09"
  cp -f "$f" "$UPLOADS_DIR/2026/09/$fname"
done

echo "=== All image files synced to uploads ==="
"""

print("Executing copy to uploads...")
stdin, stdout, stderr = ssh.exec_command(shell_cmd)
print(stdout.read().decode('utf-8', errors='ignore'))

# 2. PHPキャッシュクリア
purge_cmd = "/usr/local/php/8.2/bin/php -r \"require('web/nihongo.oscarchair.jp/wp-load.php'); if(function_exists('opcache_reset')) opcache_reset(); if(class_exists('LiteSpeed\\\\Purge')) \\LiteSpeed\\Purge::purge_all(); wp_cache_flush(); echo 'All Caches Purged!\n';\""
stdin, stdout, stderr = ssh.exec_command(purge_cmd)
print(stdout.read().decode('utf-8', errors='ignore'))

ssh.close()
print("Finished syncing full uploads and purging cache!")
