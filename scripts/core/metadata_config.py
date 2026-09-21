# -*- coding: utf-8 -*-
import os
import re

POSTS_DIR = "content/posts"

# 1. 初期記事9件のメタデータ定義
METADATA = {
    "2026-09-09-culture-shock-carb-on-carb-combos-in-japan-ramen-fried-rice-gyoza-rice-vermicelli.md": {
        "title": "カルチャーショック：餃子も炒飯もビーフンも全部「主食」！香港出身の私が驚いた日本の「炭水化物×炭水化物」文化",
        "slug": "culture-shock-carb-on-carb-combos-in-japan-ramen-fried-rice-gyoza-rice-vermicelli",
        "date": "2026-09-09T08:00:00+09:00",
        "categories": ["culture-shock"],
        "tags": ["カルチャーショック", "日本食", "炭水化物", "餃子", "食文化の違い"],
        "thumbnail": "assets/images/thumbnails/thumb-culture-carb-combo.jpg",
        "description": "香港や中華圏では炒飯も餃子もビーフンも1品で完結する「主食」。なのに日本の定食屋では「ラーメン＋半チャーハン」「餃子定食」「焼きそばパン」と主食×主食のオンパレード！？食文化の決定的な違いと魅力を徹底解説。",
        "related": [
            ("culture-shock-why-japanese-streets-are-clean-without-trash-cans", "カルチャーショック：ゴミ箱なし社会の謎"),
            ("street-japanese-izakaya-survival-guide", "街角サバイバル：居酒屋の洗礼「お通し＆生」")
        ]
    },
    "2026-09-10-culture-shock-cash-on-delivery-refused-tip-keep-the-change.md": {
        "title": "カルチャーショック：代引きで「お釣り大丈夫です」と言ったら「いやダメです！」と断られた話｜日本にチップ文化がない本当の理由",
        "slug": "culture-shock-cash-on-delivery-refused-tip-keep-the-change",
        "date": "2026-09-10T08:00:00+09:00",
        "categories": ["culture-shock"],
        "tags": ["カルチャーショック", "チップ文化", "代引き", "接客マナー", "文化の違い"],
        "thumbnail": "assets/images/thumbnails/thumb-culture-cash-on-delivery.jpg",
        "description": "海外では常識の「お釣りは取っておいて（Keep the change）」。日本の代引きで配達員さんに言ったら「1円たりとも受け取れません！」と全力で断られた！？日本人がチップを頑なに受け取らない本当の理由とおもてなし哲学。",
        "related": [
            ("kotoba-no-aya-the-trap-of-daijoubu-yes-or-no-japanese-magic-phrase", "ことばのあや：「大丈夫です」の罠"),
            ("street-japanese-convenience-store-register-survival-guide", "街角サバイバル：コンビニレジ攻防戦")
        ]
    },
    "2026-09-10-culture-shock-haircut-price-5000-yen-vs-1000-yen-cut-hong-kong-comparison.md": {
        "title": "カルチャーショック：日本の散髪、高すぎない！？香港で60ドルだった私が「5,000円カット」と「1,000円カット」の真実に納得するまで",
        "slug": "culture-shock-haircut-price-5000-yen-vs-1000-yen-cut-hong-kong-comparison",
        "date": "2026-09-10T12:00:00+09:00",
        "categories": ["culture-shock"],
        "tags": ["カルチャーショック", "美容室", "1000円カット", "物価の違い", "香港と日本"],
        "thumbnail": "assets/images/thumbnails/thumb-culture-haircut-price.jpg",
        "description": "香港なら約1,200円で切れる散髪が、日本では5,000円〜！？最初は「高すぎる！」と怯えていた香港出身のオスカーが、シャンプー・マッサージの極上ホスピタリティと1,000円カットの職人技を体験して納得した真実。",
        "related": [
            ("street-japanese-hair-salon-survival-shampoo-trap-guide", "街角サバイバル：美容室シャンプー台の試練"),
            ("culture-shock-cash-on-delivery-refused-tip-keep-the-change", "カルチャーショック：日本にチップがない理由")
        ]
    },
    "2026-09-10-japanese-comparing-sayonara-and-matane-differences-in-goodbye-expressions.md": {
        "title": "くらべてみました：「さようなら」VS「またね」の違い｜なぜ日本人は友達に「さようなら」と言わないのか？",
        "slug": "japanese-comparing-sayonara-and-matane-differences-in-goodbye-expressions",
        "date": "2026-09-10T18:00:00+09:00",
        "categories": ["comparing-japanese"],
        "tags": ["くらべてみました", "さようなら", "またね", "別れの挨拶", "日本語学習"],
        "thumbnail": "assets/images/thumbnails/thumb-kurabete-sayonara-matane.jpg",
        "description": "教科書で一番最初に習う「さようなら」。でも実際の日本人は友達や同僚にほとんど「さようなら」と言わない！？「二度と会えない永遠の別れ」を連想させる語源の歴史と、日常で飛び交う「またね・じゃあね」の温かい心理。",
        "related": [
            ("japanese-comparing-zenzen-and-mattaku-differences", "くらべてみました：「全然」VS「全く」の違い"),
            ("kotoba-no-aya-the-seven-faces-of-sumimasen", "ことばのあや：「すみません」の7変化")
        ]
    },
    "2026-09-11-kotoba-no-aya-the-trap-of-daijoubu-yes-or-no-japanese-magic-phrase.md": {
        "title": "ことばのあや：「大丈夫です」の罠｜YESなの？それともNO？日本人が連発する万能フレーズの解読術",
        "slug": "kotoba-no-aya-the-trap-of-daijoubu-yes-or-no-japanese-magic-phrase",
        "date": "2026-09-11T08:00:00+09:00",
        "categories": ["kotoba-no-aya"],
        "tags": ["ことばのあや", "大丈夫", "YESとNO", "接客日本語", "クッション言葉"],
        "thumbnail": "assets/images/thumbnails/thumb-kotoba-daijoubu-trap.jpg",
        "description": "「レシート大丈夫です」はNOなのに、「この席大丈夫です」はYES！？肯定と否定の両方で使われる日本の魔法の言葉「大丈夫」。イントネーション・手振り・表情から真意を一瞬で見分ける解読術を分かりやすく解説。",
        "related": [
            ("kotoba-no-aya-the-seven-faces-of-sumimasen", "ことばのあや：「すみません」の7変化"),
            ("street-japanese-convenience-store-register-survival-guide", "街角サバイバル：コンビニレジ攻防戦")
        ]
    },
    "2026-09-12-culture-shock-cars-stop-when-you-raise-your-hand-pedestrian-crosswalk-in-japan.md": {
        "title": "カルチャーショック：手を挙げたら車がピタッと止まってくれた！？日本の横断歩道と海外の「命がけの道路横断」",
        "slug": "culture-shock-cars-stop-when-you-raise-your-hand-pedestrian-crosswalk-in-japan",
        "date": "2026-09-12T08:00:00+09:00",
        "categories": ["culture-shock"],
        "tags": ["カルチャーショック", "横断歩道", "交通マナー", "歩行者優先", "日本と海外"],
        "thumbnail": "assets/images/thumbnails/thumb-culture-cars-stop.jpg",
        "description": "香港や海外では「車が途切れる隙を狙って命がけでダッシュ」が当たり前。なのに日本の信号のない横断歩道で右手をピッと挙げたら、車がスーッと減速して完全停止！？日本の歩行者優先文化とドライバーの優しさに感動した話。",
        "related": [
            ("culture-shock-japanese-first-graders-walk-to-school-alone-safety-and-independence", "カルチャーショック：小1の単独登校に世界が仰天"),
            ("culture-shock-why-japanese-streets-are-clean-without-trash-cans", "カルチャーショック：街中にゴミ箱がない謎")
        ]
    },
    "2026-09-13-culture-shock-japanese-first-graders-walk-to-school-alone-safety-and-independence.md": {
        "title": "カルチャーショック：小1が1人で電車に乗って登校！？海外なら親が逮捕される「日本の通学事情」に世界が仰天する理由",
        "slug": "culture-shock-japanese-first-graders-walk-to-school-alone-safety-and-independence",
        "date": "2026-09-13T08:00:00+09:00",
        "categories": ["culture-shock"],
        "tags": ["カルチャーショック", "通学", "治安", "自立心", "日本社会"],
        "thumbnail": "assets/images/thumbnails/thumb-culture-kids-school.jpg",
        "description": "大きなランドセルを背負った6歳の男の子が、親もつけずにたった1人で電車に乗って登校！？欧米や海外なら「保護者遺棄」で親が即逮捕されるレベルの光景が、なぜ日本では安全に成立しているのか？地域社会の見守りネットワークの秘密。",
        "related": [
            ("culture-shock-cars-stop-when-you-raise-your-hand-pedestrian-crosswalk-in-japan", "カルチャーショック：手を挙げたら車が止まる横断歩道"),
            ("street-japanese-station-ticket-gate-dungeon-guide", "街角サバイバル：駅改札ダンジョン攻略法")
        ]
    },
    "2026-09-14-kotoba-no-aya-particles-zo-and-ze-anime-vs-real-life-japanese.md": {
        "title": "ことばのあや：終助詞「ぞ」「ぜ」の話｜アニメで毎日聞くのに、なぜ現実の日本人は使わないのか？",
        "slug": "kotoba-no-aya-particles-zo-and-ze-anime-vs-real-life-japanese",
        "date": "2026-09-14T08:00:00+09:00",
        "categories": ["kotoba-no-aya"],
        "tags": ["ことばのあや", "終助詞", "ぞとぜ", "アニメ日本語", "役割語"],
        "thumbnail": "assets/images/thumbnails/thumb-kotoba-zo-ze.jpg",
        "description": "「行くぞ！」「うまいぜ！」アニメで主人公たちが毎日かっこよく連発する終助詞「ぞ」「ぜ」。でも現実の日本人が居酒屋や職場で使ったら超不自然！？アニメ独自のキャラクター記号（役割語）と現実会話での正しい使い分け。",
        "related": [
            ("kotoba-no-aya-the-seven-faces-of-sumimasen", "ことばのあや：「すみません」の7変化"),
            ("japanese-comparing-zenzen-and-mattaku-differences", "くらべてみました：「全然」VS「全く」の違い")
        ]
    },
    "2026-09-15-japanese-comparing-ageru-kureru-morau-differences-in-giving-and-receiving.md": {
        "title": "くらべてみました：「あげる」VS「くれる」VS「もらう」の違い｜なぜ日本語には「GIVE」が2つもあるのか？",
        "slug": "japanese-comparing-ageru-kureru-morau-differences-in-giving-and-receiving",
        "date": "2026-09-15T08:00:00+09:00",
        "categories": ["comparing-japanese"],
        "tags": ["くらべてみました", "あげる", "くれる", "もらう", "授受動詞", "日本語文法"],
        "thumbnail": "assets/images/thumbnails/thumb-kurabete-ageru-kureru.jpg",
        "description": "英語なら「give」1語で済むのに、日本語ではなぜ「あげる」と「くれる」で単語が分かれるのか？矢印が内側（自分側）に向くか外側に向くか、日本人の「ウチとソト」の人間関係がそのまま言葉になった授受表現の完全攻略ガイド。",
        "related": [
            ("japanese-comparing-zenzen-and-mattaku-differences", "くらべてみました：「全然」VS「全く」の違い"),
            ("kotoba-no-aya-sonosetsu-wa-doumo", "ことばのあや：「その節はどうも…」の謎")
        ]
    }
}

print(f"Loaded {len(METADATA)} metadata configurations.")
