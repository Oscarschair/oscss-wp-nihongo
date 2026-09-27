import os
import re
import sys
import paramiko
from PIL import Image

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 1. Load env
env = {}
with open('.env.deploy', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(env['SSH_HOST'], int(env['SSH_PORT']), env['SSH_USER'], env['SSH_PASS'], look_for_keys=False, allow_agent=False)
sftp = ssh.open_sftp()

remote_theme_base = "web/nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo"

# 2. Upload images to theme assets
image_files = [
    # (local_path, remote_subpath)
    ("assets/images/thumbnails/thumb-kotoba-shouchidesu-trap.jpg", "assets/images/thumbnails/thumb-kotoba-shouchidesu-trap.jpg"),
    ("assets/images/thumbnails/thumb-kotoba-shouchidesu-trap.webp", "assets/images/thumbnails/thumb-kotoba-shouchidesu-trap.webp"),
    ("assets/images/thumbnails/thumb-street-city-hall-rpg.jpg", "assets/images/thumbnails/thumb-street-city-hall-rpg.jpg"),
    ("assets/images/thumbnails/thumb-street-city-hall-rpg.webp", "assets/images/thumbnails/thumb-street-city-hall-rpg.webp"),
    ("assets/images/thumbnails/thumb-comparing-rashii-souda-youda.jpg", "assets/images/thumbnails/thumb-comparing-rashii-souda-youda.jpg"),
    ("assets/images/thumbnails/thumb-comparing-rashii-souda-youda.webp", "assets/images/thumbnails/thumb-comparing-rashii-souda-youda.webp"),
    ("assets/images/posts/kotoba-shouchidesu-office-confusion.jpg", "assets/images/posts/kotoba-shouchidesu-office-confusion.jpg"),
    ("assets/images/posts/kotoba-shouchidesu-office-confusion.webp", "assets/images/posts/kotoba-shouchidesu-office-confusion.webp"),
    ("assets/images/posts/street-city-hall-counter-guide.jpg", "assets/images/posts/street-city-hall-counter-guide.jpg"),
    ("assets/images/posts/street-city-hall-counter-guide.webp", "assets/images/posts/street-city-hall-counter-guide.webp"),
    ("assets/images/posts/comparing-rashii-souda-youda-weather.jpg", "assets/images/posts/comparing-rashii-souda-youda-weather.jpg"),
    ("assets/images/posts/comparing-rashii-souda-youda-weather.webp", "assets/images/posts/comparing-rashii-souda-youda-weather.webp"),
]

print("=== Uploading Images via SFTP ===")
for loc, rem_sub in image_files:
    remote_full = f"{remote_theme_base}/{rem_sub}"
    sftp.put(loc, remote_full)
    print(f"[SFTP OK] {loc} -> {remote_full}")

sftp.close()
ssh.close()
print("Images uploaded successfully!")
