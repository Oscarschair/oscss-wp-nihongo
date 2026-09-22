import os
import re
import sys
import jaconv
from janome.tokenizer import Tokenizer

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

tokenizer = Tokenizer()

def align_ruby(surface, reading_kata):
    if not re.search(r'[\u4e00-\u9faf]', surface):
        return surface
    
    reading_hira = jaconv.kata2hira(reading_kata)
    
    # Prefix match
    pre_len = 0
    while pre_len < len(surface) and pre_len < len(reading_hira):
        if surface[pre_len] == reading_hira[pre_len] and not re.match(r'[\u4e00-\u9faf]', surface[pre_len]):
            pre_len += 1
        else:
            break
            
    # Suffix match
    suf_len = 0
    while suf_len < (len(surface) - pre_len) and suf_len < (len(reading_hira) - pre_len):
        if surface[-1 - suf_len] == reading_hira[-1 - suf_len] and not re.match(r'[\u4e00-\u9faf]', surface[-1 - suf_len]):
            suf_len += 1
        else:
            break
            
    prefix = surface[:pre_len]
    suffix = surface[len(surface) - suf_len:] if suf_len > 0 else ''
    kanji_part = surface[pre_len:len(surface) - suf_len if suf_len > 0 else len(surface)]
    rt_part = reading_hira[pre_len:len(reading_hira) - suf_len if suf_len > 0 else len(reading_hira)]
    
    if not re.search(r'[\u4e00-\u9faf]', kanji_part) or not rt_part:
        return surface

    return f'{prefix}<ruby>{kanji_part}<rt>{rt_part}</rt></ruby>{suffix}'

def process_text_segment(text):
    tokens = tokenizer.tokenize(text)
    out = []
    for tok in tokens:
        if re.search(r'[\u4e00-\u9faf]', tok.surface):
            out.append(align_ruby(tok.surface, tok.reading))
        else:
            out.append(tok.surface)
    return "".join(out)

def ruby_markdown(md_text):
    # Frontmatter separation
    parts = re.split(r'^---\s*$', md_text, maxsplit=2, flags=re.MULTILINE)
    if len(parts) >= 3:
        header = f"---{parts[1]}---\n"
        body = parts[2]
    else:
        header = ""
        body = md_text

    placeholders = []
    def repl(m):
        idx = len(placeholders)
        placeholders.append(m.group(0))
        return f"__PROTECTED_{idx}__"

    body = re.sub(r'```[\s\S]*?```', repl, body)
    body = re.sub(r'`[^`]+`', repl, body)
    body = re.sub(r'!\[.*?\]\(.*?\)', repl, body)
    body = re.sub(r'<ruby>[\s\S]*?</ruby>', repl, body)
    
    def link_url_repl(m):
        txt = m.group(1)
        url = m.group(2)
        idx = len(placeholders)
        placeholders.append(url)
        return f"[{txt}](__PROTECTED_{idx}__)"
    body = re.sub(r'\[(.*?)\]\((.*?)\)', link_url_repl, body)
    body = re.sub(r'<[^>]+>', repl, body)

    segments = re.split(r'(__PROTECTED_\d+__)', body)
    processed = []
    for seg in segments:
        if re.match(r'^__PROTECTED_\d+__$', seg):
            processed.append(seg)
        else:
            lines = seg.split('\n')
            proc_lines = []
            for l in lines:
                if l.strip().startswith('|') and l.strip().endswith('|'):
                    cells = l.split('|')
                    proc_cells = []
                    for c in cells:
                        if re.match(r'^\s*:?-+:?\s*$', c):
                            proc_cells.append(c)
                        else:
                            proc_cells.append(process_text_segment(c))
                    proc_lines.append("|".join(proc_cells))
                else:
                    proc_lines.append(process_text_segment(l))
            processed.append("\n".join(proc_lines))

    result_body = "".join(processed)
    for idx, orig in enumerate(placeholders):
        result_body = result_body.replace(f"__PROTECTED_{idx}__", orig)

    return header + result_body

raw_article = """---
title: "街角サバイバル：カフェ注文の波状攻撃｜「店内？」「手渡し？」「マグカップ？」…次々と繰り出される謎質問を突破せよ！"
slug: "street-japanese-cafe-order-survival-mug-or-paper-guide"
date: "2026-09-21 08:00:00"
categories:
  - "street-japanese"
tags:
  - "街角サバイバル"
  - "カフェ"
  - "注文"
  - "接客日本語"
  - "実用会話"
description: "日本のカフェで直面する連続質問トラップ！「店内ですか？」「商品は手渡しで？」「マグカップでよろしいですか？（途中で出たい時はどうする！？）」。レジ前でフリーズしないための攻略法と実用コマンドを徹底解説！"
thumbnail: "assets/images/thumbnails/thumb-street-cafe-order-rpg.jpg"
---
日本の街を歩いていて、「ちょっと喉が渇いたな」「おしゃれなカフェで一休みしよう」とお店のドアを開けたあなた。

美味しそうなコーヒーの香りに包まれてレジカウンターの前に立ち、元気よく**「アイスコーヒーを1つください！」**と注文しました。

「ふう、これで美味しいコーヒーが飲めるぞ……！」と安心したのも束の間。

カウンターの店員さんが、満面の笑みでこう切り込んできます。

> **店員さん：**「かしこまりました！ **店内でお召し上がりですか？ お持ち帰りですか？**」  
> **あなた：**「えっ、あ、店内で……」  
> **店員さん：**「ありがとうございます！ **サイズはいかがなさいますか？**」  
> **あなた：**「あ、Mサイズで……」  
> **店員さん：**「ホットですか、アイスですか？」  
> **あなた：**「（さっきアイスって言ったのに……！）アイスで！」  
> **店員さん：**「**お飲み物はマグカップ（グラス）でお出ししてよろしいでしょうか？**」  
> **あなた：**「（マグカップ・・！？ え、グラスじゃダメなの？ 途中で出たくなったら持って帰れないの！？）」  
> **店員さん：**「**お砂糖やミルクはお使いになりますか？**」  
> **あなた：**「あ、大丈夫です……」  
> **店員さん：**「あと、ご一緒にこちらのクッキーはいかがですか？ **こちらは商品は手渡しでよろしいでしょうか？**」  
> **あなた：**「…………（手渡し・・！？ 逆に手渡し以外何があるんだ！？）」  

――**はい、全滅（GAME OVER）です。**

ただアイスコーヒーを1杯飲みたいだけなのに、なぜ日本のカフェやテイクアウト店のレジでは、まるで**「知恵比べ」のような連続質問の波状攻撃**が飛んでくるのでしょうか！？

今回は、日本で暮らす外国人や旅行者が必ず一度はフリーズする**「カフェ注文の重要関門」の攻略法**を完全伝授します！

---

## 1. 第1の関門：税率トラップ「店内ですか？ お持ち帰りですか？」

日本のカフェやファストフードで注文する際、最初にほぼ100%聞かれるのがこの質問です。

* 🗣️ **「店内でお召し上がりですか？ それともお持ち帰りですか？」**
* 🗣️ **「店内ですか？ テイクアウトですか？」**

実はこれ、単なる場所の確認ではありません。
日本には2019年から導入された**「軽減税率」**という制度があり、**店内で飲むと消費税10%**、**持ち帰ると消費税8%**と、法律上値段が変わってしまうのです！

店員さんも国のルールに従って、レジのボタンを押し分けるために絶対に確認しなければならない重要ミッションなのです。

```
【 勇者の選択コマンド 】
--------------------------------------------------
▶ 店内で飲むとき　 ➔ 「店内で」
▶ 持ち帰りたいとき ➔ 「持ち帰りで」 / 「テイクアウトで」
--------------------------------------------------
```

> 💡 **オスカーの攻略アドバイス**  
> 店員さんに聞かれる前に、最初の注文で**「店内で、アイスラテのMサイズを1つください」**と先制攻撃を仕掛けると、一瞬でスムーズにクリアできます！

---

## 2. 第2の関門：【最大の謎】「商品は手渡しでよろしいでしょうか？」

![カフェのレジで「商品は手渡しでよろしいでしょうか？」と聞かれ、「手渡し…？ 逆に手渡し以外に何があるんだ！？」と激しく困惑するオスカー](https://nihongo.oscarchair.jp/wp-content/themes/oscss-wp-nihongo/assets/images/posts/cafe-takeout-as-is-tape-confusion.jpg)

カフェのレジ横で売られているスコーンやクッキーを追加したとき、あるいはパン屋さんやコンビニでおにぎりやパンを買ったとき。

店員さんが商品を手に持ち、笑顔でこう聞いてきます。

> **店員さん：**「こちら、**商品は手渡しでよろしいでしょうか？**」

この質問を聞いたとき、私は本気で頭の中に「？？？」が浮かびました。

> **オスカー：**「手渡し……！？ **逆に手渡し以外に何があるんだ……！？** 投げてよこすのか、空からドローンで落とされるのか……！？」

### 🔍 「手渡し」の本当の意味
安心してください！ パンを素手で握りしめて放り投げられるわけではありません（笑）。

日本の「商品は手渡しでよろしいでしょうか？」の真意は、
**「持ち帰り用のレジ袋には入れず、商品をそのまま（パッケージのまま）お渡ししてよろしいですか？（袋は不要ですか？）」**
という意味だったのです！

2020年にレジ袋が全国一律で有料化されて以来、日本の接客現場では**「袋代がかかりますが、レジ袋に入れますか？ それとも袋なしでお渡ししていいですか？」**を短縮・丁寧にした結果、**「商品は手渡しでよろしいでしょうか？」**や**「そのままお渡ししてよろしいですか？」**という独特の言い回しが定着しました。

外国人からすると「レジに立って買い物している以上、手渡しするのは当たり前だろう（笑）」と思ってしまうのですが、日本の接客用語では**「手渡し ＝ レジ袋なしでそのまま渡す」**という暗黙の共通認識（お約束）になっているのです。

```
【 「手渡し」への対応コマンド 】
--------------------------------------------------
▶ 袋がいらないとき（カバンにすぐ入れる・手に持って歩ける）
  ➔ 「はい、手渡しで大丈夫です！」 / 「はい、そのままで！」

▶ 袋に入れてほしいとき（手がふさがっている・雨の日）
  ➔ 「袋を1枚お願いします」（※数円かかります）
  ➔ 「小分けの紙袋に入れてもらえますか？」
--------------------------------------------------
```

---

## 3. 第3の関門：【容器トラップ】「マグカップ（グラス）でお出ししてよろしいでしょうか？」

「店内で飲みます」と答えた直後、スターバックスやドトール、タリーズなどで高確率で飛んでくるのがこの質問です。

* 🗣️ **「お飲み物はマグカップでお出ししてよろしいですか？」**
* 🗣️ **「アイスのお飲み物ですが、グラスでお作りしてよろしいでしょうか？」**

外国人旅行者にとって、これも意外な混乱ポイントです。

> **外国人読者：**「えっ、マグカップと紙コップで何か値段や味が変わるの……？」  
> **外国人読者：**「もし急な用事が入って、飲みきれずに途中で出たくなったら、マグカップだと持って帰れないじゃん！」  

### 🔍 なぜ容器の種類を聞いてくるの？
日本の大手カフェチェーンでは、プラスチックゴミや使い捨て紙コップを削減する**「SDGs・環境配慮（リユース食器推進）」**に力を入れています。
そのため、「店内でゆっくり過ごすお客様には、できる限り洗って再利用できる陶器のマグカップやガラスグラスで提供する」というオペレーションが標準化されているのです。

もちろん、マグカップやグラスの方が保温性・保冷性が高く、口当たりも良いため美味しく飲めるというメリットもあります。

### 🚨 途中で持ち帰りたくなったときのサバイバル術
ただし！ 「30分だけ座って飲んで、残りは歩きながら飲みたい」「急いでいてすぐに店を出るかもしれない」という時にマグカップで受け取ってしまうと、外に持ち出せなくなってしまいます。

そんな時は、**遠慮せずに「紙コップ（テイクアウト用カップ）」を希望してOK**です！

```
【 容器の選択コマンド 】
--------------------------------------------------
▶ 店内でゆっくり落ち着いて飲むとき
  ➔ 「はい、マグカップでお願いします！」
  ➔ 「グラスで大丈夫です！」

▶ 途中で持ち帰る可能性がある・急いでいるとき
  ➔ 「途中で出たいので、紙コップ（テイクアウトカップ）でお願いします！」
  ➔ 「持ち歩きたいので、使い捨てのカップにしてもらえますか？」
--------------------------------------------------
```
※もしマグカップで受け取ってしまった後で急に店を出なければならなくなった場合でも、レジで**「すみません、急ぎで出ることになったので、持ち帰り用のカップに移し替えてもらえますか？」**と頼めば、親切にプラスチックカップや紙コップに入れ替えてくれますよ！

---

## 4. 第4の関門：【気配りトラップ】「お砂糖やミルクはお使いになりますか？」

ドリンクの準備が進むと、最後に聞かれるのが甘さとミルクの確認です。

* 🗣️ **「お砂糖やミルクはお使いになりますか？」**
* 🗣️ **「シロップやミルクはおつけしますか？」**

海外のカフェでは「砂糖やミルクは受取カウンター横の台（コンディメントバー）から自分で勝手に取って入れる」スタイルが多いですが、日本のカフェでは**レジで店員さんが直接手渡ししてくれるお店**もたくさんあります。

ブラックで飲みたいときは、迷わず**「大丈夫です」**または**「いらないです」**と笑顔で伝えましょう！

---

## 5. 街角サバイバル実戦対照表（日本語 ↔ 広東語 ↔ 英語）

日本のカフェやテイクアウト店で遭遇する決まり文句を、対照表にまとめました。スマホに保存して、注文前にサッと予習しておきましょう！

| 店員のセリフ（日本語） | 広東語の意味（解説） | 英語 | あなたの推奨返答コマンド |
| :--- | :--- | :--- | :--- |
| **店内でお召し上がりですか？** | 喺度食（堂食）定係外賣？ | For here or to go? | <strong>「店内で」</strong> / <strong>「持ち帰りで」</strong> |
| **そのままお渡ししていいですか？** | 就咁俾你得唔得？（唔使膠袋，淨係貼貼紙） | Without a bag? (As is) | <strong>「そのままで大丈夫です！」</strong> / <strong>「袋1枚ください」</strong> |
| **マグカップでお出ししていいですか？** | 用瓷杯/玻璃杯上得唔得？ | Is a mug/glass OK? | <strong>「マグカップで」</strong> / <strong>「紙コップでお願いします」</strong> |
| **サイズはいかがなさいますか？** | 想要咩size？（S/M/L） | What size would you like? | <strong>「Mサイズで」</strong> / <strong>「トールで」</strong> |
| **お砂糖やミルクはご利用ですか？** | 要唔要糖同奶精？ | Do you need sugar or milk? | <strong>「大丈夫です」</strong>（不要時） / <strong>「お願いします」</strong> |
| **レシートはご利用ですか？** | 要唔要收據？ | Would you like your receipt? | <strong>「大丈夫です」</strong> / <strong>「お願いします」</strong> |

---

## 6. オスカーのひとことメモ

> 💬 **オスカー**  
> 香港の茶餐廳（チャーチャーンテーン）やカフェだと、「凍檸茶、唔該！（アイスレモンティーよろしく！）」と言えば、甘さや持ち帰りかどうかが阿吽の呼吸でササッと進みますよね。
>   
> 一方で、日本のカフェは「店内か持ち帰りか」「サイズ」「温めるか」「マグか紙コップか」「袋に入れるか」まで、**お客様の意向を1ミリも外さないように徹底的に確認してくれる**のが特徴です。
>   
> 最初はその質問の多さに圧倒されて「ただコーヒーを飲みたいだけなのに……！」とパニックになりがちですが、理由を知れば**「日本らしいきめ細やかな配慮とエコ意識」**が感じられて愛おしくなってきます。
>   
> 合言葉は**「店内で・そのままで大丈夫です！」**（持ち帰りたいときは「紙コップで！」）。  
> この三大コマンドさえ唱えられれば、あなたも今日から日本のカフェやテイクアウト店の常連マスターです！

---

[oscss_series category="street-japanese" title="🗺️ 「街角サバイバル」連載シリーズ"]

[oscss_related slug="street-japanese-convenience-store-register-survival-guide" label="あわせて読みたい：第1弾コンビニ編"]
[oscss_related slug="street-japanese-izakaya-survival-guide" label="街角サバイバル：居酒屋の洗礼"]
"""

# Apply universal rubies
rubied_full = ruby_markdown(raw_article)

# Title ruby separately
parts = re.split(r'^---\s*$', rubied_full, maxsplit=2, flags=re.MULTILINE)
fm = parts[1]
body = parts[2]

title_match = re.search(r'^(title:\s*["\'])(.*?)(["\']\s*)$', fm, flags=re.MULTILINE)
if title_match:
    orig_t = title_match.group(2)
    rubied_t = process_text_segment(orig_t)
    fm = fm.replace(title_match.group(0), f'title: "{rubied_t}"\n', 1)

final_content = f"---{fm}---{body}"

target_path = "content/posts/2026-09-21-street-japanese-cafe-order-survival-mug-or-paper-guide.md"
with open(target_path, "w", encoding="utf-8") as f:
    f.write(final_content)

print("Successfully updated cafe article with full rubies and mug-or-paper section!")
