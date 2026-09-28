import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 945})
        url = "https://nihongo.oscarchair.jp/kotoba-no-aya-how-to-use-the-final-particle-yone-for-smooth-conversation/?v=" + str(asyncio.get_event_loop().time())
        await page.goto(url, wait_until="networkidle")
        await asyncio.sleep(2)
        
        # 1. 記事ヘッダー全体をキャプチャ
        await page.screenshot(path="post_127_fixed.png", clip={"x": 0, "y": 0, "width": 1280, "height": 700})
        
        # バッジのBoundingRectを取得
        badge_rect = await page.evaluate('''() => {
            const b = document.querySelector('.c-post-meta__categories .c-badge--category');
            if (!b) return null;
            const r = b.getBoundingClientRect();
            return { x: r.x, y: r.y, w: r.width, h: r.height, text: b.innerText };
        }''')
        print("Category Badge Rect:", badge_rect)
        
        await browser.close()
        print("Finished verification.")

asyncio.run(run())
