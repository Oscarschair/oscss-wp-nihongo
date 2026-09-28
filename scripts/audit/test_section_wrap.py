import re
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def wrap_entry_sections(content):
    # すでにc-entry__sectionがある場合は属性補完のみ
    if '<section' in content and 'c-entry__section' in content:
        def repl_sec(m):
            attrs = m.group(1)
            if 'data-ad-exclude' not in attrs:
                attrs += ' data-ad-exclude="true"'
            if 'google-anno-skip' not in attrs:
                attrs = re.sub(r'class=(["\'])(.*?)\1', r'class=\1\2 google-anno-skip no-ads adsbygoogle-noab\1', attrs)
            return f'<section{attrs}>'
        return re.sub(r'<section([^>]*)>', repl_sec, content, flags=re.IGNORECASE)

    # 見出し H2 または c-vocab-box で分割する
    # パターン: (<!-- wp:heading.*?-->\s*)?<h2\b.*?>.*?</h2>(\s*<!-- /wp:heading -->)?
    # または (<!-- wp:html -->\s*)?<div class="c-vocab-box">
    
    # 区切り位置の正規表現
    # H2見出しの開始、または c-vocab-box の開始
    split_pattern = r'(?=(?:<!-- wp:heading.*?-->\s*)?<h2\b|(?:<!-- wp:html -->\s*)?<div class="c-vocab-box">)'
    parts = re.split(split_pattern, content, flags=re.DOTALL | re.IGNORECASE)
    
    sections = []
    for i, part in enumerate(parts):
        part_trimmed = part.strip()
        if not part_trimmed:
            continue
        
        # クラス名の決定
        if 'c-vocab-box' in part:
            sec_class = "c-entry__section c-entry__section--vocab google-anno-skip no-ads adsbygoogle-noab"
        elif i == 0 and not re.search(r'<h2\b', part, re.I):
            sec_class = "c-entry__section c-entry__section--lead google-anno-skip no-ads adsbygoogle-noab"
        else:
            sec_class = "c-entry__section google-anno-skip no-ads adsbygoogle-noab"
            
        sections.append(f'<section class="{sec_class}" data-ad-exclude="true">\n{part_trimmed}\n</section>')
        
    return '\n\n'.join(sections)

test_html = """
<p>こんにちは、オスカーです。今日は日本語の勉強です。</p>
<blockquote>田中先輩の一言</blockquote>

<!-- wp:heading -->
<h2>1. よねの基本</h2>
<!-- /wp:heading -->
<p>よねは相手の同意を求める言葉です。</p>
<p>例えばこんな感じです。</p>

<h2>2. 失敗しやすいシチュエーション</h2>
<p>目上の人には使えません。</p>

<div class="c-vocab-box">
  <h3>🎯 今回の語彙</h3>
  <div class="c-vocab-grid">...</div>
</div>

<h2>まとめ</h2>
<p>上手に使いましょう。</p>
"""

res = wrap_entry_sections(test_html)
print(res)
