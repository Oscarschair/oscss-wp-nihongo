import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 375, "height": 812})
        page = await context.new_page()
        await page.goto("https://nihongo.oscarchair.jp/manga/manga-01-daijoubu-trap/?nocache=1790552700", wait_until="networkidle")
        await page.screenshot(path="sp_manga_fixed_375.png")
        await page.screenshot(path="sp_manga_fixed_375_full.png", full_page=True)
        await browser.close()
        print("Screenshots taken successfully!")

asyncio.run(check())
