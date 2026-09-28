import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 375, "height": 812})
        page = await context.new_page()
        
        # 1. Check normal post
        await page.goto("https://nihongo.oscarchair.jp/kotoba-no-aya-the-trap-of-daijoubu-yes-or-no-japanese-magic-phrase/", wait_until="networkidle")
        await page.screenshot(path="sp_normal_post_full.png", full_page=True)
        
        # 2. Check manga post
        await page.goto("https://nihongo.oscarchair.jp/manga/manga-01-daijoubu-trap/", wait_until="networkidle")
        await page.screenshot(path="sp_manga_post_full.png", full_page=True)
        
        await browser.close()

asyncio.run(check())
