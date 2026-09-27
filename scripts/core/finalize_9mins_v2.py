import sys
import re
import math

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def get_stats(t):
    plain = re.sub(r'---.*?---', '', t, flags=re.DOTALL)
    plain = re.sub(r'<[^>]+>', '', plain)
    plain = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', plain)
    plain = re.sub(r'\s+', '', plain)
    return len(plain), math.ceil(len(plain)/500)

# 10/13
with open('content/posts/2026-10-13-kotoba-no-aya-is-shouchidesu-wrong-business-japanese-trap.md', 'r', encoding='utf-8') as f:
    text_1013 = f.read()

extra_1013 = """
---

## 5. 就活・転職で一目置かれる！「内定承諾」の神返信テンプレート

就職活動や転職で志望企業から「内定のご連絡」を受け取った際、あまりの嬉しさにチャット感覚で「了解です！」や「承知です！」と返信してしまうと、入社前からマナーを疑われてしまいます。

```text
件名：内定のご連絡に対する御礼とお引き受けの件（クルマ）
宛名：株式会社グローバルソリューションズ
      人事部　採用担当　佐藤様

拝啓
貴社におかれましては、ますますご清栄のこととお慶び申し上げます。
選考を受けさせていただいておりましたクルマでございます。

このたびは、内定のご通知をいただき、誠にありがとうございました。
選考を通じて貴社の素晴らしいビジョンや社員の皆様の温かさに触れ、
ぜひ貴社の一員として貢献したいと強く願っておりました。
提示いただきました労働条件を慎重に確認し、
謹んで内定をお引き受け（承諾）いたしたく存じます。

ご期待に添えるよう、入社までに一層の自己研鑽に励む所存でございます。
今後の手続きや書類提出に関しまして、ご指示を仰げますと幸いです。
何卒よろしくお願い申し上げます。
敬具
```
* 💡 **ポイント**：内定通知のような重大な局面では、「承知いたしました」よりもさらに一段格式高い「謹んでお引き受けいたします」「承諾いたしたく存じます」を用いると、人事担当者からの信頼度が最高ランクになります。
"""

if "## 5. 就活・転職で一目置かれる" not in text_1013:
    text_1013 = text_1013.replace('## 5. 外国人学習者がハマりやすい', extra_1013.strip() + '\n\n---\n\n## 6. 外国人学習者がハマりやすい')
    text_1013 = text_1013.replace('## 6. 実践！場面別のロールプレイング', '## 7. 実践！場面別のロールプレイング')
    text_1013 = text_1013.replace('## 7. 日本の職場で好感度を上げる', '## 8. 日本の職場で好感度を上げる')
    text_1013 = text_1013.replace('## 8. 理解度チェック！クイズに挑戦', '## 9. 理解度チェック！クイズに挑戦')
    text_1013 = text_1013.replace('## 9. 読者からの疑問をスッキリ解決', '## 10. 読者からの疑問をスッキリ解決')
    text_1013 = text_1013.replace('## 10. まとめと本日の重要キーワード', '## 11. まとめと本日の重要キーワード')
    with open('content/posts/2026-10-13-kotoba-no-aya-is-shouchidesu-wrong-business-japanese-trap.md', 'w', encoding='utf-8') as f:
        f.write(text_1013.strip() + '\n')

# 10/14
with open('content/posts/2026-10-14-street-japanese-city-hall-resident-registration-dungeon-guide.md', 'r', encoding='utf-8') as f:
    text_1014 = f.read()

extra_1014 = """
---

## 6. 困った時に身を助ける！窓口レスキューフレーズ5選とマイナンバーの罠

市役所の窓口で言葉が聞き取れなかったり、想定外の事態が起きた時に、落ち着いて職員に助けを求めるための5つのレスキューフレーズです。

1. **「恐れ入りますが、もう少しゆっくり話していただけますか？」**
   * 役所の担当者は早口で説明しがちです。恥ずかしがらずにゆっくり話してもらいましょう。
2. **「漢字の読み方がわからないので、フリガナをふっていただけますか？」**
   * 申請書の難しい項目名（世帯主、本籍、続柄など）に鉛筆でフリガナを書いてもらうと、驚くほどスラスラ記入できます。
3. **「館内にコピー機はありますか？」**
   * 在留カードや賃貸契約書のコピーが必要になった場合、市役所内の売店やフロアの片隅に1枚10円のコピー機が必ず設置されています。
4. **「この手続きは、次回いつまでに更新に来ればいいですか？」**
   * 在留期間の更新やマイナンバーカードの更新期限について、その場で確認しておくと安心です。
5. **「英語（外国語）の記入見本はありますか？」**
   * ほとんどの自治体で、英語・中国語・韓国語・ベトナム語などで書かれた「記入例見本」が用意されています。

### ⚠️ 要注意！マイナンバーカードの「電子証明書」失効トラップ
引っ越しをして市役所で住所変更を行うと、マイナンバーカード表面の新住所印字だけでなく、**「署名用電子証明書（英数字6〜16桁の暗証番号）」が法律上自動的に失効**してしまいます！
確定申告（e-Tax）やマイナポータルでの行政手続きをスマホから行うためには、窓口で**「電子証明書の再発行（更新）も一緒にお願いします」**と必ず伝えて、暗証番号を再設定してもらいましょう。これを行わないと、後日コンビニ交付やオンライン手続きが使えなくなってしまいます。
"""

if "## 6. 困った時に身を助ける" not in text_1014:
    text_1014 = text_1014.replace('## 6. 実践ロールプレイング', extra_1014.strip() + '\n\n---\n\n## 7. 実践ロールプレイング')
    text_1014 = text_1014.replace('## 7. 市役所を出た後にやるべき', '## 8. 市役所を出た後にやるべき')
    text_1014 = text_1014.replace('## 8. 理解度チェック！市役所クイズ', '## 9. 理解度チェック！市役所クイズ')
    text_1014 = text_1014.replace('## 9. 外国人住民必見', '## 10. 外国人住民必見')
    text_1014 = text_1014.replace('## 10. まとめと本日の重要キーワード', '## 11. まとめと本日の重要キーワード')
    with open('content/posts/2026-10-14-street-japanese-city-hall-resident-registration-dungeon-guide.md', 'w', encoding='utf-8') as f:
        f.write(text_1014.strip() + '\n')

print("=== Final Verification ===")
for p, fpath in [("10/13", "content/posts/2026-10-13-kotoba-no-aya-is-shouchidesu-wrong-business-japanese-trap.md"),
                 ("10/14", "content/posts/2026-10-14-street-japanese-city-hall-resident-registration-dungeon-guide.md"),
                 ("10/15", "content/posts/2026-10-15-japanese-comparing-rashii-souda-youda-differences.md")]:
    with open(fpath, 'r', encoding='utf-8') as f:
        t = f.read()
    chars, mins = get_stats(t)
    print(f"{p}: {chars} chars -> 読了目安: 約{mins}分")
