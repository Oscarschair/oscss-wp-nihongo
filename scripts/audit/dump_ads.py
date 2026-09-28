import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 375, 'height': 667})
        url = 'https://nihongo.oscarchair.jp/street-japanese-hair-salon-survival-shampoo-trap-guide/'
        await page.goto(url, wait_until='networkidle')
        await asyncio.sleep(2)
        
        ad_info = await page.evaluate('''() => {
            const elements = document.querySelectorAll('[class*="adsbygoogle"], [id*="google_ads"], [class*="google-auto-placed"], ins, iframe[id*="aswift"], [class*="ad-"], [id*="ad-"]');
            return Array.from(elements).map(el => {
                const r = el.getBoundingClientRect();
                return {
                    tag: el.tagName,
                    id: el.id,
                    className: el.className,
                    x: r.x,
                    y: r.y,
                    width: r.width,
                    height: r.height,
                    parentTag: el.parentElement ? el.parentElement.tagName : '',
                    parentId: el.parentElement ? el.parentElement.id : '',
                    parentClass: el.parentElement ? el.parentElement.className : ''
                };
            });
        }''')
        
        print(f"Total ad matching elements on SP: {len(ad_info)}")
        with open('sp_ads_dump.json', 'w', encoding='utf-8') as f:
            json.dump(ad_info, f, ensure_ascii=False, indent=2)
            
        await browser.close()
        print("Dumped to sp_ads_dump.json")

asyncio.run(run())
