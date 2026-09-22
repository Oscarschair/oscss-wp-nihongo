import os, glob, subprocess

# リネーム対象マッピング (旧アンダースコア名 -> 新ハイフン名)
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

print("=== 1. Git mv for thumbnails ===")
for old_name, new_name in MAPPINGS.items():
    old_path = os.path.join("assets/images/thumbnails", old_name)
    new_path = os.path.join("assets/images/thumbnails", new_name)
    if os.path.exists(old_path):
        subprocess.run(["git", "mv", old_path, new_path], check=True)
        print(f"Renamed: {old_name} -> {new_name}")

print("\n=== 2. Update markdown post frontmatter ===")
posts = glob.glob("content/posts/*.md")
for p in posts:
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
    
    orig = content
    for old_name, new_name in MAPPINGS.items():
        content = content.replace(old_name, new_name)
        
    if content != orig:
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated post: {os.path.basename(p)}")

print("\nAll local renames and markdown updates completed successfully!")
