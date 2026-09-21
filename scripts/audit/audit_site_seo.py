import urllib.request
import urllib.parse
import json
import re
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

urls_to_test = [
    ("トップページ", "https://nihongo.oscarchair.jp/"),
    ("カテゴリー: 街角サバイバル", "https://nihongo.oscarchair.jp/category/street-japanese/"),
    ("カテゴリー: くらべてみました", "https://nihongo.oscarchair.jp/category/comparing/"),
    ("カテゴリー: ことばのあや", "https://nihongo.oscarchair.jp/category/kotoba-no-aya/"),
    ("カテゴリー: カルチャーショック", "https://nihongo.oscarchair.jp/category/culture-shock/"),
    ("記事: コンビニのレジ攻防戦", "https://nihongo.oscarchair.jp/street-japanese-convenience-store-register-survival-guide/"),
    ("記事: 日本の散髪代", "https://nihongo.oscarchair.jp/culture-shock-haircut-price-5000-yen-vs-1000-yen-cut-hong-kong-comparison/"),
    ("robots.txt", "https://nihongo.oscarchair.jp/robots.txt"),
    ("sitemap.xml", "https://nihongo.oscarchair.jp/sitemap.xml")
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

print("=== 🚀 サイト全体SEO自動監査スタート ===\n")

for label, url in urls_to_test:
    print(f"--------------------------------------------------")
    print(f"🌐 【{label}】: {url}")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as res:
            status = res.status
            content_type = res.headers.get('Content-Type', '')
            raw = res.read()
            html = raw.decode('utf-8', errors='ignore')
            print(f"HTTP Status: {status} | Content-Type: {content_type}")
            
            if 'html' not in content_type:
                print(f"Non-HTML content (length: {len(raw)} bytes)")
                continue

            soup = BeautifulSoup(html, 'html.parser')

            # 1. Title
            title_tag = soup.find('title')
            title_text = title_tag.text.strip() if title_tag else "なし"
            print(f"1. Title ({len(title_text)}文字): {title_text}")

            # 2. Meta Description
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            desc_text = desc_tag['content'].strip() if desc_tag and 'content' in desc_tag.attrs else "なし"
            print(f"2. Description ({len(desc_text)}文字): {desc_text[:60]}..." if len(desc_text) > 60 else f"2. Description: {desc_text}")

            # 3. Canonical
            canonical_tag = soup.find('link', attrs={'rel': 'canonical'})
            canonical_href = canonical_tag['href'] if canonical_tag and 'href' in canonical_tag.attrs else "なし"
            print(f"3. Canonical: {canonical_href}")

            # 4. Robots
            robots_tag = soup.find('meta', attrs={'name': 'robots'})
            robots_content = robots_tag['content'] if robots_tag and 'content' in robots_tag.attrs else "なし"
            print(f"4. Robots: {robots_content}")

            # 5. OGP & Twitter
            og_title = soup.find('meta', property='og:title')
            og_img = soup.find('meta', property='og:image')
            tw_card = soup.find('meta', attrs={'name': 'twitter:card'})
            print(f"5. OGP Title: {'あり' if og_title else 'なし'} | OGP Image: {og_img['content'] if og_img else 'なし'}")
            print(f"   Twitter Card: {tw_card['content'] if tw_card else 'なし'}")

            # 6. Headings
            h1s = [h.text.strip() for h in soup.find_all('h1')]
            h2s = [h.text.strip() for h in soup.find_all('h2')]
            h3s = [h.text.strip() for h in soup.find_all('h3')]
            print(f"6. Headings: H1={len(h1s)}件, H2={len(h2s)}件, H3={len(h3s)}件")
            if len(h1s) != 1:
                print(f"   ⚠️ WARNING: H1が1件ではありません: {h1s}")
            else:
                print(f"   H1: {h1s[0]}")

            # 7. JSON-LD
            json_lds = soup.find_all('script', type='application/ld+json')
            print(f"7. JSON-LD: {len(json_lds)}ブロック")
            for j in json_lds:
                try:
                    data = json.loads(j.string)
                    schema_type = data.get('@type', 'Unknown')
                    print(f"   - Schema Type: {schema_type}")
                except Exception as je:
                    print(f"   - Schema Parse Error: {je}")

            # 8. Images without alt
            imgs = soup.find_all('img')
            missing_alt = [img.get('src', '') for img in imgs if not img.get('alt')]
            print(f"8. Images: Total={len(imgs)} | Missing alt={len(missing_alt)}")
            if missing_alt:
                print(f"   ⚠️ Missing alt images: {missing_alt[:3]}")

    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")

print("\n=== 監査終了 ===")
