import paramiko, os

with open('.env.deploy', 'r', encoding='utf-8') as f:
    env = dict(l.strip().split('=', 1) for l in f if '=' in l and not l.startswith('#'))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

MAPPINGS = {
    "thumb_street_cafe_order_rpg.jpg": "thumb-street-cafe-order-rpg.jpg",
    "thumb_street_cafe_order_rpg.webp": "thumb-street-cafe-order-rpg.webp",
    "thumb_street_convenience_register.jpg": "thumb-street-convenience-register.jpg",
    "thumb_street_convenience_register.webp": "thumb-street-convenience-register.webp",
    "thumb_street_haircut_rpg.jpg": "thumb-street-haircut-rpg.jpg",
    "thumb_street_haircut_rpg.webp": "thumb-street-haircut-rpg.webp",
    "thumb_street_izakaya_rpg.jpg": "thumb-street-izakaya-rpg.jpg",
    "thumb_street_izakaya_rpg.webp": "thumb-street-izakaya-rpg.webp",
    "thumb_street_onsen_sento_rpg.jpg": "thumb-street-onsen-sento-rpg.jpg",
    "thumb_street_onsen_sento_rpg.webp": "thumb-street-onsen-sento-rpg.webp",
    "thumb_street_station_gate_rpg.jpg": "thumb-street-station-gate-rpg.jpg",
    "thumb_street_station_gate_rpg.webp": "thumb-street-station-gate-rpg.webp",
    "thumb_street_umbrella_stand_rpg.jpg": "thumb-street-umbrella-stand-rpg.jpg",
    "thumb_street_umbrella_stand_rpg.webp": "thumb-street-umbrella-stand-rpg.webp",
}

print("=== 1. Upload new hyphen files to theme & uploads, remove old underscore files ===")
for old_name, new_name in MAPPINGS.items():
    local_path = os.path.join("assets/images/thumbnails", new_name)
    remote_theme_new = f"web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/thumbnails/{new_name}"
    remote_theme_old = f"web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/thumbnails/{old_name}"
    
    # Upload new file
    print(f"Uploading {new_name}...")
    sftp.put(local_path, remote_theme_new)
    
    # Remove old theme file if exists
    try:
        sftp.remove(remote_theme_old)
        print(f"  Removed old theme file: {old_name}")
    except:
        pass

sftp.close()

# 2. Server shell: Copy to uploads and update DB
shell_cmd = """
THEME_THUMB=~/web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/thumbnails
UPLOADS=~/web/nihongo.oscarchair.jp/wp-content/uploads

for f in thumb-street-*.jpg thumb-street-*.webp; do
  if [ -f "$THEME_THUMB/$f" ]; then
    # Find matching directory in uploads (2026/09 etc)
    find "$UPLOADS" -type d -name "2026" -o -name "09" | while read d; do
      cp -u "$THEME_THUMB/$f" "$d/" 2>/dev/null || true
    done
    cp -u "$THEME_THUMB/$f" "$UPLOADS/" 2>/dev/null || true
  fi
done

echo "Server files synced!"
"""
stdin, stdout, stderr = ssh.exec_command(shell_cmd)
print(stdout.read().decode('utf-8', errors='ignore'))

ssh.close()
print("Done uploading and syncing files to server!")
