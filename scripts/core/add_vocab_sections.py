import re

# 1. 2026-10-13
fp13 = 'content/posts/2026-10-13-kotoba-no-aya-is-shouchidesu-wrong-business-japanese-trap.md'
with open(fp13, 'r', encoding='utf-8') as f:
    c13 = f.read()

vocab13 = """
---

## 🎯 今回の語彙（重要ボキャブラリー）

この学習ノートに登場した、覚えておきたい重要日本語：

* **承知（しょうち）** 【JLPT N3】
  * 意味：acknowledgment, consent
  * 例文：上司からの指示に対して「承知いたしました」と返信した。
* **了解（りょうかい）** 【JLPT N3】
  * 意味：understanding, approval (peer/subordinate)
  * 例文：「了解です」は同僚や後輩に対して使う言葉で、目上の人には適さない。
* **かしこまる（畏まる）** 【JLPT N1】
  * 意味：to obey respectfully, to understand (humble)
  * 例文：大切なお客様からの依頼に「かしこまりました」と深く頭を下げた。
* **謙譲語（けんじょうご）** 【JLPT N2】
  * 意味：humble language
  * 例文：自分の動作をへりくだることで相手に敬意を表すのが謙譲語である。
"""

target13 = "![オフィスのチャット返信で戸惑うクルマ](assets/images/posts/kotoba-shouchidesu-confusion.jpg)\n\n---"
replacement13 = f"![オフィスのチャット返信で戸惑うクルマ](assets/images/posts/kotoba-shouchidesu-confusion.jpg)\n{vocab13}\n---"

if target13 in c13:
    c13 = c13.replace(target13, replacement13, 1)
    with open(fp13, 'w', encoding='utf-8') as f:
        f.write(c13)
    print("Added vocab to 10-13")
else:
    print("Target not found in 10-13")


# 2. 2026-10-14
fp14 = 'content/posts/2026-10-14-street-japanese-city-hall-resident-registration-dungeon-guide.md'
with open(fp14, 'r', encoding='utf-8') as f:
    c14 = f.read()

vocab14 = """
---

## 🎯 今回の語彙（重要ボキャブラリー）

この学習ノートに登場した、覚えておきたい重要日本語：

* **転入届（てんにゅうとどけ）** 【JLPT N2】
  * 意味：notification of moving in
  * 例文：引っ越してから14日以内に市役所へ行って転入届を提出しなければならない。
* **転出証明書（てんしゅつしょうめいしょ）** 【JLPT N2】
  * 意味：certificate of moving out
  * 例文：前の住所の役所で発行してもらった転出証明書を窓口に提出した。
* **在留カード（ざいりゅうかーど）** 【JLPT N3】
  * 意味：residence card
  * 例文：市役所の窓口で在留カードを提示し、裏面に新しい住所を印字してもらった。
* **窓口（まどぐち）** 【JLPT N3】
  * 意味：service counter, contact window
  * 例文：番号札を取ってロビーの椅子で待っていると、3番の窓口から呼び出された。
"""

target14 = "この<ruby>記事<rt>きじ</rt></ruby>を<ruby>読<rt>よ</rt></ruby>めば、<ruby>迷子<rt>まいご</rt></ruby>にならず、<ruby>書類<rt>しょるい</rt></ruby>の<ruby>不備<rt>ふび</rt></ruby>で<ruby>出直<rt>でなお</rt></ruby>すこともなく、<ruby>最短<rt>さいたん</rt></ruby><ruby>時間<rt>じかん</rt></ruby>でスマートに<ruby>手続<rt>てつづ</rt></ruby>きを<ruby>完了<rt>かんりょう</rt></ruby>できますよ！\n\n---"
replacement14 = f"この<ruby>記事<rt>きじ</rt></ruby>を<ruby>読<rt>よ</rt></ruby>めば、<ruby>迷子<rt>まいご</rt></ruby>にならず、<ruby>書類<rt>しょるい</rt></ruby>の<ruby>不備<rt>ふび</rt></ruby>で<ruby>出直<rt>でなお</rt></ruby>すこともなく、<ruby>最短<rt>さいたん</rt></ruby><ruby>時間<rt>じかん</rt></ruby>でスマートに<ruby>手続<rt>てつづ</rt></ruby>きを<ruby>完了<rt>かんりょう</rt></ruby>できますよ！\n{vocab14}\n---"

if target14 in c14:
    c14 = c14.replace(target14, replacement14, 1)
    with open(fp14, 'w', encoding='utf-8') as f:
        f.write(c14)
    print("Added vocab to 10-14")
else:
    print("Target not found in 10-14")


# 3. 2026-10-15
fp15 = 'content/posts/2026-10-15-japanese-comparing-rashii-souda-youda-differences.md'
with open(fp15, 'r', encoding='utf-8') as f:
    c15 = f.read()

vocab15 = """
---

## 🎯 今回の語彙（重要ボキャブラリー）

この学習ノートに登場した、覚えておきたい重要日本語：

* **推量（すいりょう）** 【JLPT N1】
  * 意味：conjecture, guess, estimation
  * 例文：話し手の主観的な推量と、第三者からの伝聞では文末表現が異なる。
* **伝聞（でんぶん）** 【JLPT N1】
  * 意味：hearsay, rumor
  * 例文：天気予報で「明日は雨が降るそうだ」と伝聞の形で聞いた。
* **五感（ごかん）** 【JLPT N1】
  * 意味：the five senses
  * 例文：自分の目で直接見た変化の兆候には「〜そうだ」が使われる。
* **兆候（ちょうこう）** 【JLPT N1】
  * 意味：sign, indication, omen
  * 例文：今にも雨が降り出しそうな雲行きを見て、急いで洗濯物を取り込んだ。
"""

target15 = "この3<ruby>兄弟<rt>きょうだい</rt></ruby>の<ruby>違<rt>ちが</rt></ruby>いをスッキリ<ruby>解き明<rt>ときあ</rt></ruby>かしましょう！\n\n---"
replacement15 = f"この3<ruby>兄弟<rt>きょうだい</rt></ruby>の<ruby>違<rt>ちが</rt></ruby>いをスッキリ<ruby>解き明<rt>ときあ</rt></ruby>かしましょう！\n{vocab15}\n---"

if target15 in c15:
    c15 = c15.replace(target15, replacement15, 1)
    with open(fp15, 'w', encoding='utf-8') as f:
        f.write(c15)
    print("Added vocab to 10-15")
else:
    print("Target not found in 10-15")
