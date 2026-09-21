import urllib.request
import re
import json

urls = [
    "https://nihongo.oscarchair.jp/",
    "https://nihongo.oscarchair.jp/street-japanese-convenience-store-register-survival-guide/",
    "https://nihongo.oscarchair.jp/culture-shock-carb-on-carb-combos-in-japan-ramen-fried-rice-gyoza-rice-vermicelli/",
    "https://nihongo.oscarchair.jp/kotoba-no-aya-particles-zo-and-ze-anime-vs-real-life-japanese/",
    "https://nihongo.oscarchair.jp/japanese-comparing-sayonara-and-matane-differences-in-goodbye-expressions/"
]

results = []

for url in urls:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        results.append({"url": url, "error": str(e)})
        continue

    # 1. Title Tag
    title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else ""

    # 2. Meta Description
    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
    if not desc_match:
        desc_match = re.search(r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']', html, re.IGNORECASE)
    desc = desc_match.group(1).strip() if desc_match else ""

    # 3. Canonical
    canonical_match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\'](.*?)["\']', html, re.IGNORECASE)
    canonical = canonical_match.group(1).strip() if canonical_match else ""

    # 4. Robots
    robots_match = re.search(r'<meta\s+name=["\']robots["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
    robots = robots_match.group(1).strip() if robots_match else ""

    # 5. OGP & Twitter
    og_title_match = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
    og_title = og_title_match.group(1).strip() if og_title_match else ""

    og_image_match = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
    og_image = og_image_match.group(1).strip() if og_image_match else ""

    tw_card_match = re.search(r'<meta\s+name=["\']twitter:card["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
    tw_card = tw_card_match.group(1).strip() if tw_card_match else ""

    # 6. JSON-LD
    json_ld_matches = re.findall(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', html, re.IGNORECASE | re.DOTALL)
    json_ld_types = []
    json_ld_errors = []
    for jtext in json_ld_matches:
        try:
            jdata = json.loads(jtext)
            if isinstance(jdata, list):
                for item in jdata:
                    json_ld_types.append(item.get("@type", "Unknown"))
            elif isinstance(jdata, dict):
                if "@graph" in jdata:
                    for item in jdata["@graph"]:
                        json_ld_types.append(item.get("@type", "Unknown"))
                else:
                    json_ld_types.append(jdata.get("@type", "Unknown"))
        except Exception as err:
            json_ld_errors.append(str(err))

    # 7. Headings
    h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
    h2_matches = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.IGNORECASE | re.DOTALL)
    h3_matches = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.IGNORECASE | re.DOTALL)

    # 8. Images without alt
    imgs = re.findall(r'<img\s+[^>]*>', html, re.IGNORECASE)
    imgs_without_alt = []
    for img in imgs:
        if 'alt=' not in img.lower() or re.search(r'alt=["\']\s*["\']', img, re.IGNORECASE):
            imgs_without_alt.append(img[:80])

    # 9. Related shortcodes rendered
    blog_cards = re.findall(r'class=["\'][^"\']*c-blog-card[^"\']*["\']', html, re.IGNORECASE)

    # 10. Author box
    has_author_box = "c-author-box" in html
    author_name = "オスカー" if "オスカー" in html else "None"

    results.append({
        "url": url,
        "status": status,
        "title": title,
        "title_len": len(title),
        "desc": desc,
        "desc_len": len(desc),
        "canonical": canonical,
        "robots": robots,
        "og_title": og_title,
        "og_image": og_image,
        "tw_card": tw_card,
        "json_ld_types": json_ld_types,
        "json_ld_errors": json_ld_errors,
        "h1_count": len(h1_matches),
        "h2_count": len(h2_matches),
        "h3_count": len(h3_matches),
        "imgs_count": len(imgs),
        "imgs_without_alt_count": len(imgs_without_alt),
        "blog_cards_count": len(blog_cards),
        "has_author_box": has_author_box,
        "has_kuruma": "クルマ" in html
    })

print(json.dumps(results, ensure_ascii=False, indent=2))
