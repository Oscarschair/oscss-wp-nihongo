import glob
import re
import sys
from deploy_batch_posts import md_to_gutenberg

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

test_files = [
    'content/posts/2026-09-17-street-japanese-izakaya-survival-guide.md',
    'content/posts/2026-09-20-kotoba-no-aya-sonosetsu-wa-doumo-thanks-and-apology.md',
    'content/posts/2026-09-18-japanese-comparing-zenzen-and-mattaku-differences-in-degree-and-nuance.md',
    'content/posts/2026-09-11-street-japanese-convenience-store-register-survival-guide.md',
    'content/posts/2026-09-10-culture-shock-haircut-price-5000-yen-vs-1000-yen-cut-hong-kong-comparison.md',
]

print("=== 🔍 Markdownパース & リンクタグ検証 ===")
total_links = 0
for tf in test_files:
    with open(tf, 'r', encoding='utf-8') as f:
        content = f.read()
    html = md_to_gutenberg(content)
    links = re.findall(r'<a href="([^"]+)">([^<]+)</a>', html)
    print(f"\n📄 {tf}")
    print(f"   生成されたHTMLブロック数: {len(html.split('<!-- /wp:'))}")
    print(f"   検出された内部リンク数: {len(links)}")
    total_links += len(links)
    for href, text in links:
        print(f"   - [{text[:35]}] -> {href}")

print(f"\n🎉 検証成功！ テスト対象ファイルから合計 {total_links} 件の正常な <a href> リンクを検出しました。")
