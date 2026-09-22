import urllib.request
import re

slugs = [
    "street-japanese-convenience-store-register-survival-guide",
    "street-japanese-hair-salon-survival-shampoo-trap-guide",
    "street-japanese-station-ticket-gate-dungeon-guide",
    "street-japanese-izakaya-survival-guide",
    "street-japanese-cafe-order-survival-mug-or-paper-guide",
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for slug in slugs:
    url = f"https://nihongo.oscarchair.jp/{slug}/"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    
    cocoon_count = html.count('wp:cocoon-blocks')
    balloons = len(re.findall(r'<div class="c-balloon c-balloon--[lr]">', html))
    cmd_boxes = len(re.findall(r'<div class="c-command-box">', html))
    
    # check series box
    series_match = re.search(r'<aside class="c-series-box">.*?</aside>', html, re.DOTALL)
    if series_match:
        sb = series_match.group(0)
        escaped_sb = sb.count('&lt;ruby&gt;')
        real_sb = sb.count('<ruby>')
        sb_status = f"c-series-box OK (escaped={escaped_sb}, real={real_sb})"
    else:
        sb_status = "c-series-box NONE"
        
    print(f"[{slug[:30]}] Cocoon:{cocoon_count}, Balloon:{balloons}, CmdBox:{cmd_boxes}, {sb_status}")
