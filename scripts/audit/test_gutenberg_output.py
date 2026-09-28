import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from scripts.core.gutenberg_parser import parse_markdown_to_gutenberg_full

f = 'content/posts/2026-09-10-culture-shock-cash-on-delivery-refused-tip-keep-the-change.md'
html = parse_markdown_to_gutenberg_full(f)
print(f'Parsed length: {len(html)} chars')
print('Has vocab box in html:', '<div class="c-vocab-box"' in html)
print('Has wp:html block:', '<!-- wp:html -->' in html)
print('Ruby count:', html.count('<ruby>'))
print('H2 tag count:', html.count('<h2 class="wp-block-heading">'))
print('H3 tag count:', html.count('<h3 class="wp-block-heading">'))
