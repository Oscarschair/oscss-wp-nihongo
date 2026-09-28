import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 375, "height": 667})
        url = "https://nihongo.oscarchair.jp/street-japanese-hair-salon-survival-shampoo-trap-guide/"
        await page.goto(url, wait_until="networkidle")
        
        # 画面幅とドキュメント幅
        body_scroll_w = await page.evaluate("document.body.scrollWidth")
        doc_scroll_w = await page.evaluate("document.documentElement.scrollWidth")
        inner_w = await page.evaluate("window.innerWidth")
        print(f"Viewport width: {inner_w}, body scrollWidth: {body_scroll_w}, doc scrollWidth: {doc_scroll_w}")
        
        # 375px を超えている要素を全て特定
        overflow_elements = await page.evaluate('''() => {
            const elements = document.querySelectorAll('*');
            const bad = [];
            for (let el of elements) {
                const rect = el.getBoundingClientRect();
                if (rect.right > window.innerWidth || el.scrollWidth > window.innerWidth + 1) {
                    bad.push({
                        tagName: el.tagName,
                        className: el.className,
                        id: el.id,
                        rectRight: rect.right,
                        rectWidth: rect.width,
                        scrollWidth: el.scrollWidth,
                        outerHTML: el.outerHTML.substring(0, 100)
                    });
                }
            }
            return bad;
        }''')
        
        print(f"Total overflowing elements: {len(overflow_elements)}")
        for i, el in enumerate(overflow_elements[:15]):
            print(f"[{i}] {el['tagName']} class='{el['className']}' id='{el['id']}' rectRight={el['rectRight']} rectWidth={el['rectWidth']} scrollWidth={el['scrollWidth']}")
            print(f"     HTML: {el['outerHTML']}")
            
        await browser.close()

asyncio.run(run())
