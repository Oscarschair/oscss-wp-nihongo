# -*- coding: utf-8 -*-
import requests
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Fetch all post URLs from sitemap or WP API
res = requests.get('https://nihongo.oscarchair.jp/wp-json/wp/v2/posts?per_page=100')
posts = res.json()
print(f"Total published posts from API: {len(posts)}")

problem_posts = []

for p in posts:
    slug = p['slug']
    content_html = p['content']['rendered']
    
    # Check if there is raw markdown list vocab (e.g. <ul><li>...【JLPT...)
    has_plain_list_vocab = False
    if 'JLPT' in content_html and ('<li>' in content_html or '・' in content_html):
        # Check if it is inside c-vocab-box or outside
        # Remove c-vocab-box from content
        no_box = re.sub(r'<div class="c-vocab-box"[\s\S]*?</div>\s*</div>\s*</div>', '', content_html)
        if 'JLPT' in no_box and ('意味：' in no_box or '意味:' in no_box):
            has_plain_list_vocab = True
    
    # Check if c-vocab-box is missing
    has_card_box = 'c-vocab-box' in content_html
    
    if has_plain_list_vocab or not has_card_box:
        problem_posts.append((p['id'], slug, has_plain_list_vocab, has_card_box))
        print(f"[PROBLEM] ID: {p['id']} | Slug: {slug} | Has Plain List: {has_plain_list_vocab} | Has Card Box: {has_card_box}")

print(f"\nTotal problem posts found: {len(problem_posts)}")
