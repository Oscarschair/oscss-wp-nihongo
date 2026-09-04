import asyncio
import time
from playwright.async_api import async_playwright

async def verify_posts():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        # Check Post 36 (おもしろい VS おかしい)
        url_36 = "https://nihongo.oscarchair.jp/2023/02/22/japanese-comparing-interesting-and-oddy-funny-differences-in-emotional-expression/"
        print(f"Loading {url_36}...")
        await page.goto(url_36, wait_until='networkidle')
        await page.screenshot(path=r"C:\Users\user\.gemini\antigravity-ide\brain\4d088df4-e87c-4c0f-ae49-5ce9644d7e28\live_post_36_proofread.png", full_page=True)
        print("Captured Post 36!")

        # Check Post 44 (ご飯の形)
        url_44 = "https://nihongo.oscarchair.jp/2023/03/06/culture-shock-japanese-food-for-shaping-rice-find-an-authentic-chinese-restaurant/"
        print(f"Loading {url_44}...")
        await page.goto(url_44, wait_until='networkidle')
        await page.screenshot(path=r"C:\Users\user\.gemini\antigravity-ide\brain\4d088df4-e87c-4c0f-ae49-5ce9644d7e28\live_post_44_proofread.png", full_page=True)
        print("Captured Post 44!")

        # Check Post 19 (終助詞「ね」)
        url_19 = "https://nihongo.oscarchair.jp/2023/02/20/kotoba-no-aya-how-to-use-the-final-particle-ne-for-a-comfortable-conversation/"
        print(f"Loading {url_19}...")
        await page.goto(url_19, wait_until='networkidle')
        await page.screenshot(path=r"C:\Users\user\.gemini\antigravity-ide\brain\4d088df4-e87c-4c0f-ae49-5ce9644d7e28\live_post_19_proofread.png", full_page=True)
        print("Captured Post 19!")

        await browser.close()

asyncio.run(verify_posts())
