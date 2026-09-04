import asyncio
import time
from playwright.async_api import async_playwright

async def main():
    ts = int(time.time())
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # PC View
        page_pc = await browser.new_page(viewport={'width': 1280, 'height': 900})
        await page_pc.goto(f'https://nihongo.oscarchair.jp/?ts={ts}', wait_until='networkidle')
        await page_pc.evaluate('document.getElementById("latest-posts").scrollIntoView()')
        await page_pc.wait_for_timeout(1000)
        pc_path = rf'C:\Users\user\.gemini\antigravity-ide\brain\4d088df4-e87c-4c0f-ae49-5ce9644d7e28\live_grid_v3_pc_{ts}.png'
        await page_pc.screenshot(path=pc_path)
        print(f"PC Screenshot saved: {pc_path}")
        
        # SP View
        page_sp = await browser.new_page(viewport={'width': 375, 'height': 900})
        await page_sp.goto(f'https://nihongo.oscarchair.jp/?ts={ts}', wait_until='networkidle')
        await page_sp.evaluate('document.getElementById("latest-posts").scrollIntoView()')
        await page_sp.wait_for_timeout(1000)
        sp_path = rf'C:\Users\user\.gemini\antigravity-ide\brain\4d088df4-e87c-4c0f-ae49-5ce9644d7e28\live_grid_v3_sp_{ts}.png'
        await page_sp.screenshot(path=sp_path)
        print(f"SP Screenshot saved: {sp_path}")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
