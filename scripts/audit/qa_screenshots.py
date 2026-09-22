import asyncio
from playwright.async_api import async_playwright
import os

url = "https://nihongo.oscarchair.jp/street-japanese-cafe-order-survival-mug-or-paper-guide/"
output_dir = "C:/Users/user/.gemini/antigravity-ide/brain/02b30bf4-5cae-430f-8157-47a33a954999/uiux_qa"
os.makedirs(output_dir, exist_ok=True)

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # 1. Desktop (1280x900)
        page_pc = await browser.new_page(viewport={"width": 1280, "height": 900})
        await page_pc.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        # Scroll through to trigger any lazy loads
        await page_pc.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        await asyncio.sleep(1)
        await page_pc.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        await page_pc.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)

        # Check horizontal overflow on PC
        has_overflow_pc = await page_pc.evaluate("document.documentElement.scrollWidth > window.innerWidth")
        print(f"[PC] Horizontal overflow: {has_overflow_pc} (scrollWidth: {await page_pc.evaluate('document.documentElement.scrollWidth')}, innerWidth: 1280)")

        # Screenshots on PC
        await page_pc.screenshot(path=f"{output_dir}/pc_top.png")
        
        # Element screenshots on PC
        series_box = await page_pc.query_selector(".c-series-box")
        if series_box:
            await series_box.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            await series_box.screenshot(path=f"{output_dir}/pc_series_box.png")
            print("[PC] Captured series box")
            
        cmd_box = await page_pc.query_selector(".c-command-box")
        if cmd_box:
            await cmd_box.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            await cmd_box.screenshot(path=f"{output_dir}/pc_command_box.png")
            print("[PC] Captured command box")
            
        balloon = await page_pc.query_selector(".c-balloon")
        if balloon:
            await balloon.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            await balloon.screenshot(path=f"{output_dir}/pc_balloon.png")
            print("[PC] Captured balloon")

        # 2. Mobile SP (375x812 - iPhone X/12/13 mini style)
        page_sp = await browser.new_page(
            viewport={"width": 375, "height": 812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True
        )
        await page_sp.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        await page_sp.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        await asyncio.sleep(1)
        await page_sp.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        await page_sp.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)

        # Check horizontal overflow on SP
        scroll_w_sp = await page_sp.evaluate("document.documentElement.scrollWidth")
        has_overflow_sp = await page_sp.evaluate("document.documentElement.scrollWidth > window.innerWidth")
        print(f"[SP] Horizontal overflow: {has_overflow_sp} (scrollWidth: {scroll_w_sp}, innerWidth: 375)")

        await page_sp.screenshot(path=f"{output_dir}/sp_top.png")
        
        series_box_sp = await page_sp.query_selector(".c-series-box")
        if series_box_sp:
            await series_box_sp.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            await series_box_sp.screenshot(path=f"{output_dir}/sp_series_box.png")
            print("[SP] Captured series box")
            
        cmd_box_sp = await page_sp.query_selector(".c-command-box")
        if cmd_box_sp:
            await cmd_box_sp.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            await cmd_box_sp.screenshot(path=f"{output_dir}/sp_command_box.png")
            print("[SP] Captured command box")
            
        balloon_sp = await page_sp.query_selector(".c-balloon")
        if balloon_sp:
            await balloon_sp.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            await balloon_sp.screenshot(path=f"{output_dir}/sp_balloon.png")
            print("[SP] Captured balloon")

        await browser.close()
        print("All UI/UX captures completed!")

asyncio.run(run())
