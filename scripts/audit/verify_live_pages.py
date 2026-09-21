import urllib.request
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

urls = [
    'https://nihongo.oscarchair.jp/street-japanese-convenience-store-register-survival-guide/',
    'https://nihongo.oscarchair.jp/street-japanese-hair-salon-survival-shampoo-trap-guide/'
]

for url in urls:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    print('=== URL:', url, '===')
    
    # Check series box
    series_match = re.search(r'<aside class="c-series-box">[\s\S]*?</aside>', html)
    if series_match:
        print('✅ Series box found:')
        print(series_match.group(0))
    else:
        print('❌ NO Series box found!')
        
    # Check for future slugs leaking
    leaks = []
    for fslug in ['station-ticket-gate', 'izakaya-survival', 'cafe-order-survival']:
        if fslug in html:
            leaks.append(fslug)
    print('Future leaks detected (MUST BE EMPTY):', leaks)
    
    # Check related posts leak
    related_match = re.search(r'<section class="c-related-posts"[\s\S]*?</section>', html)
    if related_match:
        print('Related posts found in page.')
        for fslug in ['station-ticket-gate', 'izakaya-survival', 'cafe-order-survival']:
            if fslug in related_match.group(0):
                print(f'🚨 LEAK IN RELATED POSTS: {fslug}')
    
    # Check raw markdown asterisks
    dangling_stars = re.findall(r'\*\*[^\*]+?\*\*', html)
    print('Dangling markdown stars count:', len(dangling_stars))
    print('-' * 50)
