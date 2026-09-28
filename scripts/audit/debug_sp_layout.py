import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 375, "height": 812})
        page = await context.new_page()
        await page.goto("https://nihongo.oscarchair.jp/manga/manga-01-daijoubu-trap/?nocache=1790552100", wait_until="networkidle")
        
        # Check body scrollWidth vs clientWidth
        body_scroll = await page.evaluate("() => document.body.scrollWidth")
        body_client = await page.evaluate("() => document.body.clientWidth")
        doc_scroll = await page.evaluate("() => document.documentElement.scrollWidth")
        print(f"Viewport width: 375, body scrollWidth: {body_scroll}, clientWidth: {body_client}, doc scrollWidth: {doc_scroll}")
        
        # Find overflowing elements
        overflowing = await page.evaluate('''() => {
            const elements = document.querySelectorAll('*');
            const bad = [];
            for (const el of elements) {
                const rect = el.getBoundingClientRect();
                if (rect.right > 380 || rect.width > 380) {
                    bad.push({
                        tag: el.tagName,
                        id: el.id,
                        className: el.className,
                        width: rect.width,
                        right: rect.right
                    });
                }
            }
            return bad.slice(0, 20);
        }''')
        
        print("\nOverflowing elements:")
        for b in overflowing:
            print(b)
            
        await page.screenshot(path="sp_debug_375.png")
        await browser.close()

asyncio.run(check())
