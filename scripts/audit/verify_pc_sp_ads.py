import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        # 1. SP (375x667)
        page_sp = await browser.new_page(viewport={"width": 375, "height": 667})
        url = "https://nihongo.oscarchair.jp/street-japanese-hair-salon-survival-shampoo-trap-guide/?v=" + str(asyncio.get_event_loop().time())
        await page_sp.goto(url, wait_until="networkidle")
        await asyncio.sleep(2)
        
        sp_fixed_ads = await page_sp.evaluate('''() => {
            const list = document.querySelectorAll('.adsbygoogle-noablate, [data-ad-format*="rail"], iframe[id^="aswift_"][style*="fixed"], div[id*="aswift"][style*="fixed"], html > ins.adsbygoogle, body > ins.adsbygoogle');
            return Array.from(list).map(el => ({
                tag: el.tagName,
                display: window.getComputedStyle(el).display,
                visibility: window.getComputedStyle(el).visibility,
                w: el.getBoundingClientRect().width,
                h: el.getBoundingClientRect().height
            }));
        }''')
        print(f"SP side/fixed ads matching count: {len(sp_fixed_ads)}")
        for ad in sp_fixed_ads:
            print("  SP Ad:", ad)
            
        await page_sp.screenshot(path="sp_ad_verified.png")
        
        # 2. PC (1920x945)
        page_pc = await browser.new_page(viewport={"width": 1920, "height": 945})
        await page_pc.goto(url, wait_until="networkidle")
        await asyncio.sleep(2)
        
        pc_ads = await page_pc.evaluate('''() => {
            const list = document.querySelectorAll('iframe[id^="aswift_"], ins.adsbygoogle');
            return Array.from(list).map(el => ({
                id: el.id,
                display: window.getComputedStyle(el).display,
                x: el.getBoundingClientRect().x
            }));
        }''')
        print(f"PC total ads found: {len(pc_ads)}")
        pc_side_ads = [a for a in pc_ads if a['x'] < 300 or a['x'] > 1500]
        print(f"PC side rail ads visible: {len(pc_side_ads)}")
        for a in pc_side_ads:
            print("  PC Side Ad:", a)
            
        await page_pc.screenshot(path="pc_ad_verified.png")
        await browser.close()
        print("Verification completed successfully!")

asyncio.run(run())
