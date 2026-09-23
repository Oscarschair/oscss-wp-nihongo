import os
import shutil
from PIL import Image

image_mappings = [
    (
        r"C:\Users\user\.gemini\antigravity-ide\brain\02b30bf4-5cae-430f-8157-47a33a954999\comparing_iku_kuru_1790158406852.jpg",
        r"assets/images/posts/comparing-iku-kuru-phone-running.jpg"
    ),
    (
        r"C:\Users\user\.gemini\antigravity-ide\brain\02b30bf4-5cae-430f-8157-47a33a954999\street_delivery_scan_1790158452204.jpg",
        r"assets/images/posts/street-delivery-mailbox-qr-scan.jpg"
    ),
    (
        r"C:\Users\user\.gemini\antigravity-ide\brain\02b30bf4-5cae-430f-8157-47a33a954999\kotoba_kekkoudesu_1790158475051.jpg",
        r"assets/images/posts/kotoba-kekkoudesu-register-smile.jpg"
    ),
    (
        r"C:\Users\user\.gemini\antigravity-ide\brain\02b30bf4-5cae-430f-8157-47a33a954999\culture_hanko_counter_1790158498560.jpg",
        r"assets/images/posts/culture-hanko-counter-shachihata-rejection.jpg"
    ),
    (
        r"C:\Users\user\.gemini\antigravity-ide\brain\02b30bf4-5cae-430f-8157-47a33a954999\street_clinic_form_1790158597091.jpg",
        r"assets/images/posts/street-clinic-questionnaire-fill.jpg"
    ),
    (
        r"C:\Users\user\.gemini\antigravity-ide\brain\02b30bf4-5cae-430f-8157-47a33a954999\comparing_hazu_wake_1790158545636.jpg",
        r"assets/images/posts/comparing-hazu-wake-understanding-proof.jpg"
    ),
    (
        r"C:\Users\user\.gemini\antigravity-ide\brain\02b30bf4-5cae-430f-8157-47a33a954999\culture_expiry_discount_1790158571027.jpg",
        r"assets/images/posts/culture-expiry-discount-supermarket.jpg"
    )
]

os.makedirs("assets/images/posts", exist_ok=True)

for src, dst in image_mappings:
    if not os.path.exists(src):
        print(f"Error: source not found: {src}")
        continue
    
    # 1. Copy JPG
    shutil.copyfile(src, dst)
    print(f"Copied JPG: {dst}")
    
    # 2. Convert to WebP
    webp_dst = os.path.splitext(dst)[0] + ".webp"
    with Image.open(src) as img:
        img.save(webp_dst, "WEBP", quality=85, method=6)
    print(f"Created WebP: {webp_dst}")

print("All 7 post illustrations copied and converted to WebP successfully!")
