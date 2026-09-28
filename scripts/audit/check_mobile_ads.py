import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        iphone_se = p.devices['iPhone SE']
        browser = await p.chromium.launch()
        context = await browser.new_context(**iphone_se)
        page = await context.new_page()
        
        url = 'https://nihongo.oscarchair.jp/street-japanese-hair-salon-survival-shampoo-trap-guide/'
        await page.goto(url, wait_until='networkidle')
        await asyncio.sleep(2)
        
        scroll_w = await page.evaluate('document.documentElement.scrollWidth')
        client_w = await page.evaluate('document.documentElement.clientWidth')
        body_scroll_w = await page.evaluate('document.body.scrollWidth')
        window_w = await page.evaluate('window.innerWidth')
        
        print(f'window.innerWidth: {window_w}')
        print(f'clientWidth: {client_w}')
        print(f'documentElement.scrollWidth: {scroll_w}')
        print(f'body.scrollWidth: {body_scroll_w}')
        
        ads = await page.evaluate('''() => {
            const iframes = Array.from(document.querySelectorAll('iframe, ins.adsbygoogle, [id*="google_ads"], [class*="ad-"]'));
            return iframes.map(el => {
                const r = el.getBoundingClientRect();
                return {
                    tag: el.tagName,
                    id: el.id,
                    className: el.className,
                    width: r.width,
                    right: r.right
                };
            });
        }''')
        print(f'Total ad elements: {len(ads)}')
        for a in ads:
            if a['width'] > 375 or a['right'] > 375:
                print('OVERFLOW AD:', a)
                
        await page.screenshot(path='sp_iphone_se_actual.png')
        await browser.close()
        print('Saved sp_iphone_se_actual.png')

asyncio.run(run())
