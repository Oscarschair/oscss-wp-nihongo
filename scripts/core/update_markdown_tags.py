import glob
import re
import os

# 全39記事に対する新タグ10種類の精密割り当て
TAG_MAPPING = {
    # くらべてみました系 (8記事)
    "japanese-comparing-sayonara-and-matane-differences-in-goodbye-expressions": [
        "ニュアンスの違い", "日常会話"
    ],
    "japanese-comparing-ageru-kureru-morau-differences-in-giving-and-receiving": [
        "ニュアンスの違い", "日本語文法", "日常会話"
    ],
    "japanese-comparing-zenzen-and-mattaku-differences": [
        "ニュアンスの違い", "日常会話"
    ],
    "japanese-comparing-chotto-and-sukoshi-differences": [
        "ニュアンスの違い", "日常会話"
    ],
    "japanese-comparing-tabun-osoraku-kitto-differences": [
        "ニュアンスの違い", "日常会話"
    ],
    "japanese-comparing-futoru-futotteiru-aspect-differences": [
        "ニュアンスの違い", "日本語文法", "日常会話"
    ],
    "japanese-comparing-iku-vs-kuru-perspective-trap": [
        "ニュアンスの違い", "日本語文法", "日常会話"
    ],
    "japanese-comparing-hazu-vs-wake-nuance-differences": [
        "ニュアンスの違い", "日本語文法", "日常会話"
    ],

    # 街角サバイバル系 (11記事)
    "street-japanese-convenience-store-register-survival-guide": [
        "日常会話", "接客・レジ日本語", "生活・手続き"
    ],
    "street-japanese-hair-salon-survival-shampoo-trap-guide": [
        "日常会話", "接客・レジ日本語", "生活・手続き"
    ],
    "street-japanese-station-ticket-gate-dungeon-guide": [
        "日常会話", "街歩き・交通", "生活・手続き"
    ],
    "street-japanese-izakaya-survival-guide": [
        "日常会話", "食文化", "接客・レジ日本語"
    ],
    "street-japanese-cafe-order-survival-mug-or-paper-guide": [
        "日常会話", "食文化", "接客・レジ日本語"
    ],
    "street-japanese-onsen-sento-bath-rules-survival-guide": [
        "日常会話", "日本文化・マナー", "生活・手続き"
    ],
    "street-japanese-rainy-day-umbrella-stand-dungeon-guide": [
        "日常会話", "街歩き・交通", "日本文化・マナー"
    ],
    "street-japanese-kaitenzushi-hot-water-express-lane-survival-guide": [
        "日常会話", "食文化", "接客・レジ日本語"
    ],
    "street-japanese-ramen-ticket-machine-call-survival-guide": [
        "日常会話", "食文化", "接客・レジ日本語"
    ],
    "street-japanese-delivery-redelivery-undelivered-notice-dungeon-guide": [
        "日常会話", "生活・手続き", "日本文化・マナー"
    ],
    "street-japanese-clinic-medical-questionnaire-pharmacy-guide": [
        "日常会話", "生活・手続き"
    ],

    # ことばのあや系 (8記事)
    "kotoba-no-aya-the-trap-of-daijoubu-yes-or-no-japanese-magic-phrase": [
        "ニュアンスの違い", "日常会話", "日本文化・マナー"
    ],
    "kotoba-no-aya-particles-zo-and-ze-anime-vs-real-life-japanese": [
        "ニュアンスの違い", "日本語文法", "日常会話"
    ],
    "kotoba-no-aya-the-seven-faces-of-sumimasen": [
        "ニュアンスの違い", "日常会話", "日本文化・マナー"
    ],
    "kotoba-no-aya-sonosetsu-wa-doumo": [
        "ニュアンスの違い", "敬語・ビジネスマナー", "日本文化・マナー"
    ],
    "kotoba-no-aya-the-trap-of-tekitou-proper-or-careless": [
        "ニュアンスの違い", "日常会話", "敬語・ビジネスマナー"
    ],
    "kotoba-no-aya-tsumaranai-mono-gift-giving-psychology": [
        "ニュアンスの違い", "日本文化・マナー", "敬語・ビジネスマナー"
    ],
    "kotoba-no-aya-otsukaresama-vs-gokurousama-trap": [
        "ニュアンスの違い", "敬語・ビジネスマナー", "日本文化・マナー"
    ],
    "kotoba-no-aya-the-trap-of-kekkoudesu-yes-or-no": [
        "ニュアンスの違い", "日常会話", "敬語・ビジネスマナー"
    ],

    # カルチャーショック系 (12記事)
    "culture-shock-japanese-food-for-shaping-rice-find-an-authentic-chinese-restaurant": [
        "異文化比較・香港", "食文化", "日本文化・マナー"
    ],
    "culture-shock-carb-on-carb-combos-in-japan-ramen-fried-rice-gyoza-rice-vermicelli": [
        "異文化比較・香港", "食文化", "日本文化・マナー"
    ],
    "culture-shock-cash-on-delivery-refused-tip-keep-the-change": [
        "異文化比較・香港", "日本文化・マナー", "生活・手続き"
    ],
    "culture-shock-haircut-price-5000-yen-vs-1000-yen-cut-hong-kong-comparison": [
        "異文化比較・香港", "生活・手続き", "日本文化・マナー"
    ],
    "culture-shock-cars-stop-when-you-raise-your-hand-pedestrian-crosswalk-in-japan": [
        "異文化比較・香港", "街歩き・交通", "日本文化・マナー"
    ],
    "culture-shock-japanese-first-graders-walk-to-school-alone-safety-and-independence": [
        "異文化比較・香港", "街歩き・交通", "日本文化・マナー"
    ],
    "culture-shock-why-japanese-streets-are-clean-without-trash-cans": [
        "異文化比較・香港", "日本文化・マナー", "生活・手続き"
    ],
    "culture-shock-why-japanese-toilets-play-water-sounds-otohime": [
        "異文化比較・香港", "日本文化・マナー", "生活・手続き"
    ],
    "culture-shock-leaving-smartphone-unattended-cafe-japan": [
        "異文化比較・香港", "日本文化・マナー", "生活・手続き"
    ],
    "culture-shock-why-no-phone-calls-and-newspapers-on-japanese-trains": [
        "異文化比較・香港", "街歩き・交通", "日本文化・マナー"
    ],
    "culture-shock-hanko-seal-stamp-culture-and-signature": [
        "異文化比較・香港", "日本文化・マナー", "生活・手続き"
    ],
    "culture-shock-shoumi-kigen-vs-shouhi-kigen-discount-stickers": [
        "異文化比較・香港", "食文化", "生活・手続き"
    ],
}

updated_count = 0
for f in sorted(glob.glob('content/posts/*.md')):
    content = open(f, encoding='utf-8').read()
    fm_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        continue
    fm = fm_match.group(1)
    slug_match = re.search(r'slug:\s*["\']?([^"\']+)["\']?', fm)
    if not slug_match:
        continue
    slug = slug_match.group(1).strip()
    
    if slug not in TAG_MAPPING:
        print(f"Warning: slug not in mapping: {slug}")
        continue
    
    new_tags = TAG_MAPPING[slug]
    new_tags_block = "tags:\n" + "\n".join([f"  - {t}" for t in new_tags])
    
    # tags ブロックを置換
    if re.search(r'tags:\s*\n(?:\s*-\s*[^\n]+\n?)+', fm):
        new_fm = re.sub(r'tags:\s*\n(?:\s*-\s*[^\n]+\n?)+', new_tags_block + "\n", fm)
    else:
        new_fm = fm + "\n" + new_tags_block + "\n"
        
    new_content = content.replace(f"---\n{fm}\n---", f"---\n{new_fm}\n---")
    if new_content == content:
        # 改行の差異に対応
        new_content = re.sub(r'^---\s*\n.*?\n---', f"---\n{new_fm}\n---", content, flags=re.DOTALL)
        
    with open(f, 'w', encoding='utf-8') as out_f:
        out_f.write(new_content)
    updated_count += 1
    print(f"Updated tags for {slug}: {new_tags}")

print(f"\nSuccessfully updated tags in {updated_count} markdown files.")
