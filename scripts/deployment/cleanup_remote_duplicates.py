import paramiko

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

shell_cmd = """
THEME_DIR=~/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo
UPLOADS_DIR=~/web/nihongo.oscarchair.jp/wp-content/uploads

DUPLICATES=(
  "assets/images/posts/weather-forecast-tabun-osoraku-kitto-scale-single.jpg"
  "assets/images/posts/weather-forecast-tabun-osoraku-kitto-scale-single.webp"
  "assets/images/thumbnails/thumb-kotoba-tsumaranai-mono-melon.jpg"
  "assets/images/thumbnails/thumb-kotoba-tsumaranai-mono-melon.webp"
)

echo "=== Deleting duplicate files from theme and uploads ==="
for rel in "${DUPLICATES[@]}"; do
  fname=$(basename "$rel")
  rm -f "$THEME_DIR/$rel"
  echo "Removed from theme: $rel"
  
  find "$UPLOADS_DIR" -name "$fname" | while read u; do
    rm -f "$u"
    echo "Removed from uploads: $u"
  done
done

echo "=== Cleaned up duplicates! ==="
"""

stdin, stdout, stderr = ssh.exec_command(shell_cmd)
print(stdout.read().decode('utf-8', errors='ignore'))

ssh.close()
print("Remote duplicate cleanup finished!")
