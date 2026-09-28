import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1920, "height": 945})
        url = "https://nihongo.oscarchair.jp/street-japanese-hair-salon-survival-shampoo-trap-guide/"
        await page.goto(url, wait_until="networkidle")
        await asyncio.sleep(2)
        
        ad_info = await page.evaluate('''() => {
            const elements = document.querySelectorAll('[class*="adsbygoogle"], [id*="google_ads"], [class*="google-auto-placed"], ins, iframe[id*="aswift"]');
            return Array.from(elements).map(el => {
                const r = el.getBoundingClientRect();
                return {
                    tag: el.tagName,
                    id: el.id,
                    className: el.className,
                    x: r.x,
                    width: r.width,
                    height: r.height,
                    parentTag: el.parentElement ? el.parentElement.tagName : ''
                };
            });
        }''')
        print(f"Total ad matching elements on PC: {len(ad_info)}")
        rails = [a for a in ad_info if a['x'] < 300 or a['x'] > 1500]
        print(f"Side rail ads count on PC: {len(rails)}")
        for r in rails:
            print(r)
        await browser.close()

asyncio.run(run())
