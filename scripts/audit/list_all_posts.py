import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from scripts.core.audit_topic_duplicates import get_all_posts

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

all_p = get_all_posts()
for i, p in enumerate(all_p):
    print(f"{i+1:02d}. [{p['date'][:10]}] [{p['category']}] {p['title']}")
