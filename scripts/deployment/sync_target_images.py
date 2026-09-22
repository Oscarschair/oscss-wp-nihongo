import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)

cmd = """
THEME_DIR=~/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo
UPLOADS_DIR=~/web/nihongo.oscarchair.jp/wp-content/uploads

TARGETS=(
  thumb-culture-cafe-leaving-smartphone.jpg
  thumb-culture-cafe-leaving-smartphone.webp
  cafe-leaving-smartphone-unattended-confusion.jpg
  cafe-leaving-smartphone-unattended-confusion.webp
  thumb-street-kaitenzushi-rpg.jpg
  thumb-street-kaitenzushi-rpg.webp
  kaitenzushi-hot-water-spout-panic.jpg
  kaitenzushi-hot-water-spout-panic.webp
  thumb-kurabete-futoru-futotteiru.jpg
  thumb-kurabete-futoru-futotteiru.webp
  futoru-futotteiru-aspect-scale.jpg
  futoru-futotteiru-aspect-scale.webp
  thumb-street-ramen-ticket-rpg.jpg
  thumb-street-ramen-ticket-rpg.webp
  ramen-ticket-machine-call-confusion.jpg
  ramen-ticket-machine-call-confusion.webp
)

echo "=== Syncing latest generated images to uploads directory ==="
for f in "${TARGETS[@]}"; do
  SRC=""
  if [ -f "$THEME_DIR/assets/images/thumbnails/$f" ]; then
    SRC="$THEME_DIR/assets/images/thumbnails/$f"
  elif [ -f "$THEME_DIR/assets/images/posts/$f" ]; then
    SRC="$THEME_DIR/assets/images/posts/$f"
  fi

  if [ -n "$SRC" ]; then
    find "$UPLOADS_DIR" -name "$f" -exec cp -f "$SRC" {} \\; -print
  fi
done

# OPcache & LiteSpeed Cache パージ
/usr/local/php/8.2/bin/php -r "
define('WP_USE_THEMES', false);
require(getenv('HOME') . '/web/nihongo.oscarchair.jp/wp-load.php');
if (function_exists('opcache_reset')) { opcache_reset(); }
if (class_exists('LiteSpeed\\\\Purge')) { LiteSpeed\\\\Purge::purge_all(); }
echo 'All caches purged successfully!\n';
"
"""

stdin, stdout, stderr = ssh.exec_command(cmd)
print("STDOUT:\n", stdout.read().decode('utf-8'))
print("STDERR:\n", stderr.read().decode('utf-8'))

ssh.close()
