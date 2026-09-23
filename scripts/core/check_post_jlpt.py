import json
import re
import sys
import os
from collections import Counter

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DICT_PATH = os.path.join(os.path.dirname(__file__), '../../data/jlpt/jlpt_dictionary.json')

def load_dict():
    if not os.path.exists(DICT_PATH):
        raise FileNotFoundError(f"Dictionary not found at {DICT_PATH}")
    with open(DICT_PATH, encoding='utf-8') as f:
        data = json.load(f)
    return data['dictionary']

def analyze_text(text, word_dict=None):
    if word_dict is None:
        word_dict = load_dict()
        
    # クレンジング（HTMLタグ、ルビ、マークダウン記法除去）
    clean_text = re.sub(r'<rt>.*?</rt>', '', text)
    clean_text = re.sub(r'<[^>]+>', '', clean_text)
    clean_text = re.sub(r'https?://[^\s]+', '', clean_text)
    clean_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean_text)
    clean_text = re.sub(r'[*_#`~]', '', clean_text)

    sorted_words = sorted(word_dict.keys(), key=lambda x: len(x), reverse=True)
    
    matches = Counter()
    matched_words = {'N1': set(), 'N2': set(), 'N3': set(), 'N4': set(), 'N5': set()}
    
    for w in sorted_words:
        if len(w) < 2 and not re.search(r'[\u4e00-\u9faf]', w):
            continue
        cnt = clean_text.count(w)
        if cnt > 0:
            lvl = word_dict[w]['level']
            matches[lvl] += cnt
            matched_words[lvl].add(w)
            
    total = sum(matches.values())
    n5_cnt = matches.get('N5', 0)
    n4_cnt = matches.get('N4', 0)
    n3_cnt = matches.get('N3', 0)
    n2_cnt = matches.get('N2', 0)
    n1_cnt = matches.get('N1', 0)
    
    cum_n4 = (n5_cnt + n4_cnt) / max(1, total)
    cum_n3 = (n5_cnt + n4_cnt + n3_cnt) / max(1, total)
    adv_pct = (n2_cnt + n1_cnt) / max(1, total)
    
    n2_distinct = len(matched_words['N2'])
    n1_distinct = len(matched_words['N1'])
    
    # レベル判定
    if adv_pct >= 0.17 or n2_distinct >= 35:
        judged = "N2"
    elif adv_pct >= 0.14 and n2_distinct >= 25:
        judged = "N3〜N2"
    elif cum_n4 >= 0.52:
        judged = "N4〜N3"
    else:
        judged = "N3"
        
    return {
        'judged_level': judged,
        'total_words_matched': total,
        'matches_by_level': dict(matches),
        'unique_words_count': {lvl: len(words) for lvl, words in matched_words.items()},
        'coverage': {
            'basic_n5_n4': round(cum_n4 * 100, 1),
            'intermediate_n5_n3': round(cum_n3 * 100, 1),
            'advanced_n2_n1': round(adv_pct * 100, 1)
        },
        'sample_n2_words': list(matched_words['N2'])[:8],
        'sample_n1_words': list(matched_words['N1'])[:5]
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/core/check_post_jlpt.py <path_to_markdown_or_text>")
        sys.exit(1)
        
    target = sys.argv[1]
    if os.path.exists(target):
        with open(target, encoding='utf-8') as f:
            text = f.read()
    else:
        text = target
        
    res = analyze_text(text)
    print("=" * 50)
    print(f"🎯 判定結果: JLPT {res['judged_level']}")
    print("=" * 50)
    print(f"マッチ総語数: {res['total_words_matched']} 語")
    cov = res['coverage']
    print(f"語彙カバー率:")
    print(f"  ・基礎語彙 (N5〜N4): {cov['basic_n5_n4']}%")
    print(f"  ・中級累積 (N5〜N3): {cov['intermediate_n5_n3']}% (85%以上でN3読解可能)")
    print(f"  ・上級語彙 (N2〜N1): {cov['advanced_n2_n1']}%")
    
    u = res['unique_words_count']
    print(f"\nレベル別ユニーク語彙数:")
    print(f"  N5: {u['N5']}語 | N4: {u['N4']}語 | N3: {u['N3']}語 | N2: {u['N2']}語 | N1: {u['N1']}語")
    
    if res['sample_n2_words']:
        print(f"\n含まれる主なN2語彙: {', '.join(res['sample_n2_words'])}")
    if res['sample_n1_words']:
        print(f"含まれる主なN1語彙: {', '.join(res['sample_n1_words'])}")
    print("=" * 50)

if __name__ == '__main__':
    main()
