import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        # 1. PC (1920x945) - ユーザーの画面サイズ
        page_pc = await browser.new_page(viewport={"width": 1920, "height": 945})
        url = "https://nihongo.oscarchair.jp/street-japanese-hair-salon-survival-shampoo-trap-guide/?t=" + str(asyncio.get_event_loop().time())
        await page_pc.goto(url, wait_until="networkidle")
        
        # 記事冒頭のインラインボタンを撮影
        await page_pc.screenshot(path="pc_top_ruby_toggle.png", clip={"x": 1000, "y": 150, "width": 600, "height": 200})
        
        # スクロールしてStickyボタンを表示
        await page_pc.evaluate("window.scrollBy(0, 800)")
        await asyncio.sleep(0.5)
        
        # 右下のStickyボタン＋back-to-topボタンの領域を撮影
        await page_pc.screenshot(path="pc_sticky_ruby_toggle.png", clip={"x": 1600, "y": 700, "width": 300, "height": 230})
        
        # 2. SP (375x667)
        page_sp = await browser.new_page(viewport={"width": 375, "height": 667})
        await page_sp.goto(url, wait_until="networkidle")
        await page_sp.evaluate("window.scrollBy(0, 800)")
        await asyncio.sleep(0.5)
        await page_sp.screenshot(path="sp_sticky_ruby_toggle.png")
        
        await browser.close()
        print("Screenshots captured successfully!")

asyncio.run(run())
