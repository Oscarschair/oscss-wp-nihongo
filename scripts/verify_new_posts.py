import asyncio
from playwright.async_api import async_playwright

async def verify():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # 1. トップページの確認 (PC & SP)
        context_pc = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page_pc = await context_pc.new_page()
        print("Loading Top Page (PC)...")
        await page_pc.goto('https://nihongo.oscarchair.jp/', wait_until='networkidle')
        await page_pc.screenshot(path=r"C:\Users\user\.gemini\antigravity-ide\brain\4d088df4-e87c-4c0f-ae49-5ce9644d7e28\live_top_with_new_posts_pc.png", full_page=False)

        context_sp = await browser.new_context(viewport={'width': 375, 'height': 812})
        page_sp = await context_sp.new_page()
        print("Loading Top Page (SP)...")
        await page_sp.goto('https://nihongo.oscarchair.jp/', wait_until='networkidle')
        await page_sp.screenshot(path=r"C:\Users\user\.gemini\antigravity-ide\brain\4d088df4-e87c-4c0f-ae49-5ce9644d7e28\live_top_with_new_posts_sp.png", full_page=False)

        # 2. 新規記事① (氷水) の確認
        url_ice = "https://nihongo.oscarchair.jp/2026/09/04/culture-shock-ice-water-hospitality-in-winter-vs-hot-water-culture/"
        print(f"Loading {url_ice} (PC)...")
        await page_pc.goto(url_ice, wait_until='networkidle')
        await page_pc.screenshot(path=r"C:\Users\user\.gemini\antigravity-ide\brain\4d088df4-e87c-4c0f-ae49-5ce9644d7e28\live_post_ice_water_pc.png", full_page=True)

        # 3. 新規記事② (電車の居眠り) の確認
        url_train = "https://nihongo.oscarchair.jp/2026/09/04/culture-shock-sleeping-on-the-train-japan-safety-and-inemuri-culture/"
        print(f"Loading {url_train} (PC)...")
        await page_pc.goto(url_train, wait_until='networkidle')
        await page_pc.screenshot(path=r"C:\Users\user\.gemini\antigravity-ide\brain\4d088df4-e87c-4c0f-ae49-5ce9644d7e28\live_post_train_sleep_pc.png", full_page=True)

        await browser.close()
        print("All verification screenshots captured!")

asyncio.run(verify())
