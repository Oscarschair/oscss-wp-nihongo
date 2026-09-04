import asyncio
import time
from playwright.async_api import async_playwright

async def verify():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # 1. 氷水記事 (PC & SP)
        url_ice = "https://nihongo.oscarchair.jp/2026/09/04/culture-shock-ice-water-hospitality-in-winter-vs-hot-water-culture/"
        
        page_pc = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page_pc.goto(url_ice, wait_until='networkidle')
        await page_pc.screenshot(path=r"C:\Users\user\.gemini\antigravity-ide\brain\4d088df4-e87c-4c0f-ae49-5ce9644d7e28\live_post_ice_water_pc_final.png", full_page=True)

        page_sp = await browser.new_page(viewport={'width': 375, 'height': 812})
        await page_sp.goto(url_ice, wait_until='networkidle')
        await page_sp.screenshot(path=r"C:\Users\user\.gemini\antigravity-ide\brain\4d088df4-e87c-4c0f-ae49-5ce9644d7e28\live_post_ice_water_sp_final.png", full_page=True)

        # 2. 電車居眠り記事 (PC & SP)
        url_train = "https://nihongo.oscarchair.jp/2026/09/04/culture-shock-sleeping-on-the-train-japan-safety-and-inemuri-culture/"
        
        await page_pc.goto(url_train, wait_until='networkidle')
        await page_pc.screenshot(path=r"C:\Users\user\.gemini\antigravity-ide\brain\4d088df4-e87c-4c0f-ae49-5ce9644d7e28\live_post_train_sleep_pc_final.png", full_page=True)

        await page_sp.goto(url_train, wait_until='networkidle')
        await page_sp.screenshot(path=r"C:\Users\user\.gemini\antigravity-ide\brain\4d088df4-e87c-4c0f-ae49-5ce9644d7e28\live_post_train_sleep_sp_final.png", full_page=True)

        # 3. トップページ (PC & SP)
        ts = int(time.time())
        url_top = f"https://nihongo.oscarchair.jp/?v={ts}"
        await page_pc.goto(url_top, wait_until='networkidle')
        await page_pc.screenshot(path=r"C:\Users\user\.gemini\antigravity-ide\brain\4d088df4-e87c-4c0f-ae49-5ce9644d7e28\live_top_page_final_pc.png", full_page=True)

        await browser.close()
        print("All final verification screenshots captured!")

asyncio.run(verify())
