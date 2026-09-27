import glob
import re
import sys
import json
import base64
import paramiko

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Clean curated examples for all vocabulary words appearing in posts
curated_examples = {
    # 納得・違い・推測 (10-11)
    "納得": "先輩のわかりやすい説明を聞いて、やっと納得がいきました。",
    "違い": "似ている二つの言葉の微妙なニュアンスの違いを調べる。",
    "推測": "空に広がる黒い雨雲の様子から、大雨になると推測する。",
    
    # 期限・消費・現れる (10-12)
    "期限": "レポートの提出期限をカレンダーに書いて忘れないようにする。",
    "消費": "食品の消費期限を確認してからおいしく食べる。",
    "現れる": "夕方になると、惣菜コーナーに黄色いシールを貼る店員さんが現れる。",
    
    # 承知・謙譲・違和感 (10-13)
    "承知": "上司からの依頼に対して「承知いたしました」と快く引き受ける。",
    "謙譲": "自分の立場を低くして相手への敬意を示すのが謙譲語です。",
    "違和感": "文法的には通じるけれど、どこか不自然な言葉遣いに違和感を持つ。",
    
    # 転入・在留・窓口 (10-14)
    "転入": "引っ越しをしてから14日以内に市役所へ転入届を出しに行く。",
    "在留": "日本に暮らす外国人にとって在留カードは最も大切な身分証です。",
    "窓口": "総合案内で番号札をもらい、呼ばれるまで窓口の前で待つ。",
    
    # 推量・直感・伝聞 (10-15)
    "推量": "確かな証拠がないとき、推量の表現を使って慎重に話す。",
    "直感": "料理の湯気とにおいから、直感で「絶対においしい！」と感じた。",
    "伝聞": "友達からの噂やニュースで聞いた伝聞の情報を伝える。",

    # 不在・装備・配達 (10-07)
    "不在": "荷物の配達が来たとき、あいにく留守で不在票が入っていた。",
    "装備": "市役所に行くときは、身分証や印鑑を忘れずに装備して向かう。",
    "スト": "必要な書類をリストアップして忘れ物がないように準備する。",

    # 笑顔・レジ・結構 (10-08)
    "笑顔": "店員さんに「結構です」と断るときは、笑顔で会釈すると角が立たない。",
    "レジ": "コンビニのレジで「お箸はご利用ですか？」と聞かれた。",

    # 印鑑・文化・特注 (10-09)
    "印鑑": "銀行口座の開設や役所の手続きで重要な書類に印鑑を押す。",
    "文化": "国ごとのサインや印鑑の使い分けなど、独自の生活文化を学ぶ。",

    # 手帳・処方・問診 (10-10)
    "手帳": "病院や薬局に行くときは、お薬手帳を持参すると安心です。",
    "処方": "医師の診察を受けた後、処方箋を持って隣の調剤薬局へ向かう。",

    # 特急・注文・回転 (10-01)
    "特急": "回転寿司の特急レーンで注文したお皿がすごいスピードで届いた。",
    "注文": "タッチパネルを使って自分の好きな寿司ネタを注文する。",

    # 太る・状態・変化 (10-02)
    "太る": "「太る」は体重が増える変化を表し、「太っている」は現在の体型を表す。",
    "状態": "健康な体の状態を維持するために、毎日バランスの良い食事をとる。",
    "変化": "季節の変わり目は、気温が急激に変化するので体調に気をつける。",

    # 作法・一瞬・呪文 (10-03)
    "作法": "ラーメン店での注文や食べ終わった後の器の片付けなど、暗黙の作法がある。",
    "一瞬": "複雑なコールに戸惑ったが、一瞬の機転で「全部ふつうで」と答えた。",

    # 目上・事故・挨拶 (10-04)
    "目上": "目上の先輩や上司に対しては、「ご苦労様」ではなく「お疲れ様」を使う。",
    "事故": "言葉の選び方を一つ間違えると、思わぬコミュニケーション事故になる。",

    # 空間・沈黙・配慮 (10-05)
    "空間": "満員電車という限られた空間では、周囲の人への思いやりが大切になる。",
    "沈黙": "静かな車内での優しい沈黙を守るため、通話は控えてマナーモードにする。",

    # 相手・移動・視点 (10-06)
    "相手": "日本語の「行く」「来る」は、常に話者自身の視点から相手との距離を測る。",
    "行き": "待ち合わせ場所に遅れそうなときは「今向かっています」と連絡する。",
    "ました": "正しい敬語の使い方を一度覚えると、自信を持って話せるようになります。",

    # きっと・多分・恐らく (09-28)
    "きっと": "熱心に練習を重ねてきたから、明日の面接はきっとうまくいきます。",
    "多分": "明日は午後から雨が降る可能性が高いので、多分傘が必要になるでしょう。",
    "恐らく": "客観的なデータに基づき、このプロジェクトは恐らく成功すると予測する。",

    # 傘・絶対・盗難 (09-29)
    "絶対": "大切なビニール傘を取り違えられないよう、絶対に見分けがつく目印をつける。",

    # 席・本人・離れる (09-30)
    "本人": "カフェの席に荷物を置いたまま注文に行く光景に、外国人は誰もが驚く。",
    "離れる": "貴重品を持たずに少し席を離れても盗まれない治安の良さに感動する。"
}

def clean_example_text(word_raw, current_ex):
    # Extract kanji part of word
    clean_word = re.sub(r'<ruby>(.*?)<rt>.*?</rt></ruby>', r'\1', word_raw)
    clean_word = re.sub(r'[\(（].*?[\)）]', '', clean_word).strip()
    
    # Check if we have a curated example
    for key, val in curated_examples.items():
        if key in clean_word or clean_word in key:
            return val
            
    # Check if current_ex is dirty
    is_dirty = any(bad in current_ex for bad in ['##', '|', '」', '│', '➔', '**', '説明：']) or current_ex.startswith(('・', '※', '【', '1.', '2.', '3.', '👉')) or len(current_ex.strip()) < 8
    
    if is_dirty:
        # Fallback to a natural polite sentence using the word
        return f"日常会話やビジネスの場面で「{clean_word}」を正しく使いこなす。"
        
    return current_ex.strip()

print("Scanning and cleaning all markdown files...")
modified_files = 0

for md_path in sorted(glob.glob('content/posts/*.md')):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    match = re.search(r'(##\s*🎯?\s*.*?(?:語彙|ボキャブラリー).*?\n)(.*?)(?=\n---|\Z)', content, re.DOTALL)
    if not match:
        continue
        
    header_part = match.group(1)
    body_part = match.group(2)
    
    lines = body_part.split('\n')
    new_lines = []
    current_word = None
    file_changed = False
    
    for line in lines:
        line_str = line.strip()
        header_m = re.search(r'^\*\s*\*\*(.+?)\*\*', line_str)
        if header_m:
            current_word = header_m.group(1)
            new_lines.append(line)
            continue
            
        ex_m = re.search(r'^([*\-\s]*例文[：:])(.*)', line_str)
        if ex_m and current_word:
            prefix = ex_m.group(1)
            ex_val = ex_m.group(2).strip()
            
            cleaned_ex = clean_example_text(current_word, ex_val)
            if cleaned_ex != ex_val:
                new_lines.append(f"{prefix} {cleaned_ex}")
                file_changed = True
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
            
    if file_changed:
        new_body = '\n'.join(new_lines)
        new_content = content[:match.start(2)] + new_body + content[match.end(2):]
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        modified_files += 1
        print(f"Cleaned examples in: {md_path}")

print(f"Total markdown files cleaned: {modified_files}")
