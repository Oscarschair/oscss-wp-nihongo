import os
import glob
import re
from apply_master_vocab import VOCAB_MASTER, generate_vocab_markdown

for md in glob.glob('content/posts/*.md'):
    fname = os.path.basename(md)
    slug = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', fname).replace('.md', '')
    if slug in VOCAB_MASTER:
        with open(md, 'r', encoding='utf-8') as f:
            content = f.read()
        if '今回の語彙' not in content:
            vocab_sec = generate_vocab_markdown(VOCAB_MASTER[slug])
            # Insert before --- or before oscss_
            if '\n---' in content:
                parts = content.split('\n---', 1)
                new_content = parts[0] + "\n\n" + vocab_sec + "\n---" + parts[1]
            elif '[oscss_' in content:
                parts = content.split('[oscss_', 1)
                new_content = parts[0] + "\n\n" + vocab_sec + "\n\n[oscss_" + parts[1]
            else:
                new_content = content + "\n\n" + vocab_sec
            with open(md, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Added vocab section to {fname}")
