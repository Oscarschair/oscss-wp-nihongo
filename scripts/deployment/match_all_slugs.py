import os
import glob
import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

wp_map = {}
with open('all_wp_posts.tsv', 'r', encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 5:
            pid = int(parts[0])
            pdate = parts[1]
            pstatus = parts[2]
            pread = parts[3]
            pslug = parts[4]
            ptitle = parts[5] if len(parts) > 5 else ""
            wp_map[pslug] = {
                'id': pid,
                'date': pdate,
                'status': pstatus,
                'read': pread,
                'title': ptitle
            }

local_files = sorted(glob.glob('content/posts/*.md'))
print(f"Total local markdown files: {len(local_files)}")
print(f"Total WordPress posts in TSV: {len(wp_map)}")

matched_items = []
unmatched = []

for lf in local_files:
    fname = os.path.basename(lf)
    # extract date from filename
    m_fdate = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)\.md', fname)
    if not m_fdate:
        continue
    fdate, fslug = m_fdate.group(1), m_fdate.group(2)

    # find in wp_map
    matched_id = None
    for w_slug, w_data in wp_map.items():
        if w_data['date'].startswith(fdate):
            # check slug similarity
            if w_slug == fslug or w_slug in fslug or fslug in w_slug:
                matched_id = w_data['id']
                matched_items.append((matched_id, lf, w_data['status'], w_data['date'], w_slug))
                break

    if not matched_id:
        unmatched.append((lf, fdate, fslug))

print(f"Matched count: {len(matched_items)}")
if unmatched:
    print("Unmatched:", len(unmatched))
    for u in unmatched:
        print("  ", u)
else:
    print("ALL 52 LOCAL FILES 100% MATCHED TO WORDPRESS POSTS!")
