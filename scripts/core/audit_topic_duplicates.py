import os
import glob
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def get_all_posts():
    posts = []
    files = sorted(glob.glob('content/posts/*.md'))
    for f in files:
        with open(f, 'r', encoding='utf-8') as fp:
            content = fp.read()
        
        # Extract frontmatter
        title_m = re.search(r'title:\s*["\']?(.*?)["\']?\s*\n', content)
        slug_m = re.search(r'slug:\s*["\']?(.*?)["\']?\s*\n', content)
        date_m = re.search(r'date:\s*["\']?(.*?)["\']?\s*\n', content)
        cat_m = re.search(r'categories:\s*\n\s*-\s*["\']?(.*?)["\']?\s*\n', content)
        
        tags = []
        tags_m = re.search(r'tags:\s*\n((?:\s*-\s*["\']?.*?["\']?\s*\n)+)', content)
        if tags_m:
            for t in re.findall(r'-\s*["\']?(.*?)["\']?\s*\n', tags_m.group(1)):
                tags.append(t.strip())
                
        posts.append({
            'file': f,
            'title': title_m.group(1) if title_m else '',
            'slug': slug_m.group(1) if slug_m else '',
            'date': date_m.group(1) if date_m else '',
            'category': cat_m.group(1) if cat_m else '',
            'tags': tags
        })
    return posts

def check_proposal_duplicate(proposal_title, proposal_category='', proposal_keywords=None):
    if proposal_keywords is None:
        proposal_keywords = []
    existing = get_all_posts()
    duplicates = []
    
    # Extract substantive tokens
    prop_words = set(proposal_keywords)
    for w in re.findall(r'[\u4e00-\u9fa5]{2,}|[\u30a0-\u30ff]{2,}|[\u3040-\u309f]{3,}', proposal_title):
        if w not in ['日本', '日本人', '違い', 'なぜ', 'こと', 'もの', '完全', '徹底', '解説', 'サバイバル']:
            prop_words.add(w)

    for p in existing:
        matched_words = []
        for pw in prop_words:
            if pw in p['title'] or pw in p['slug'] or any(pw in t for t in p['tags']):
                matched_words.append(pw)
        
        # Exact keyword match or multiple word overlap
        if len(matched_words) >= 1:
            score = len(matched_words) * 20
            # Higher score for direct title inclusion
            if any(pw in p['title'] for pw in prop_words if len(pw) >= 3):
                score += 30
            duplicates.append({
                'score': score,
                'matched_words': matched_words,
                'existing_post': p
            })
            
    duplicates.sort(key=lambda x: x['score'], reverse=True)
    return duplicates

if __name__ == '__main__':
    all_p = get_all_posts()
    print(f"Total existing/scheduled posts: {len(all_p)}")
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\n=== CHECKING PROPOSAL: '{query}' ===")
        dups = check_proposal_duplicate(query)
        if dups:
            print(f"Found {len(dups)} potential overlaps:")
            for d in dups[:5]:
                ep = d['existing_post']
                print(f"  [Similarity Score: {d['score']}%] Matched: {d['matched_words']}")
                print(f"    Existing: [{ep['date'][:10]}] ({ep['category']}) {ep['title']}")
        else:
            print(">> NO DUPLICATES FOUND! Safe to propose as a new topic.")
    else:
        print("\n=== LATEST 10 SCHEDULED / PUBLISHED POSTS ===")
        for p in all_p[-10:]:
            print(f"[{p['date'][:10]}] ({p['category']}) {p['title']}")

