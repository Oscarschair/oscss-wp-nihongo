import os
import glob
import re
import json

# Master dictionary of 52 posts: slug -> [ {word, jlpt, meaning, example}, ... ]
VOCAB_MASTER = {
    "japanese-comparing-sorry-excuse-me-differences-in-apology-expressions": [
        {"word": "謝罪（しゃざい）", "jlpt": "N1", "meaning": "apology", "example": "電車を止めてしまったことについて、会社に深く謝罪した。"},
        {"word": "失礼（しつれい）", "jlpt": "N4", "meaning": "discourtesy, excuse me", "example": "先輩の部屋に入るときは「失礼します」と声をかける。"},
        {"word": "感謝（かんしゃ）", "jlpt": "N3", "meaning": "thanks, gratitude", "example": "困っているときに助けてくれた同僚に、心から感謝の気持ちを伝えた。"}
    ],
    "kotoba-no-aya-how-to-use-the-final-particle-ne-for-a-comfortable-conversation": [
        {"word": "共感（きょうかん）", "jlpt": "N1", "meaning": "empathy, sympathy", "example": "友達の悩みを聞いて、深く共感した。"},
        {"word": "同意（どうい）", "jlpt": "N3", "meaning": "agreement, consent", "example": "会議で提案された新しい企画に、全員が同意した。"},
        {"word": "相槌（あいづち）", "jlpt": "N1", "meaning": "chiming in, nodding along", "example": "相手の話を熱心に聞きながら、適切な相槌を打つ。"}
    ],
    "japanese-comparing-interesting-and-oddy-funny-differences-in-emotional-expression": [
        {"word": "興味（きょうみ）", "jlpt": "N4", "meaning": "interest (in something)", "example": "日本のアニメや文化に強い興味を持っています。"},
        {"word": "感情（かんじょう）", "jlpt": "N3", "meaning": "emotion, feeling", "example": "嬉しいときや悲しいときの感情を、素直に言葉で表現する。"},
        {"word": "表現（ひょうげん）", "jlpt": "N3", "meaning": "expression, presentation", "example": "日本語にはニュアンスの細かな違いを表す豊かな表現が多い。"}
    ],
    "japanese-comparing-scholarships-in-japan-and-overseas-different-meaning-with-same-word": [
        {"word": "奨学金（しょうがくきん）", "jlpt": "N2", "meaning": "scholarship, student loan", "example": "大学に進学するために、返済不要の奨学金を申請した。"},
        {"word": "返済（へんさい）", "jlpt": "N1", "meaning": "repayment, reimbursement", "example": "卒業後に毎月少しずつ奨学金を返済していく予定です。"},
        {"word": "制度（せいど）", "jlpt": "N3", "meaning": "system, institution", "example": "留学生を支援するための新しい制度が発表された。"}
    ],
    "culture-shock-japanese-food-for-shaping-rice-find-an-authentic-chinese-restaurant": [
        {"word": "定食（ていしょく）", "jlpt": "N3", "meaning": "set meal, combo", "example": "お昼休みに近くの食堂で日替わり定食を注文した。"},
        {"word": "本格的（ほんかくてき）", "jlpt": "N2", "meaning": "authentic, genuine", "example": "横浜の中華街で、本格的な四川料理を味わった。"},
        {"word": "おかず（おかず）", "jlpt": "N3", "meaning": "side dish", "example": "白いご飯によく合う、味の濃いおかずが好きです。"}
    ],
    "kotoba-no-aya-how-to-use-the-final-particle-yo-for-effective-conversation": [
        {"word": "主張（しゅちょう）", "jlpt": "N2", "meaning": "claim, assertion", "example": "自分の意見を相手に伝えるときは、感情的にならずに主張する。"},
        {"word": "伝達（でんたつ）", "jlpt": "N1", "meaning": "transmission, delivery", "example": "重要な連絡事項を、部署のメンバー全員に正確に伝達した。"},
        {"word": "配慮（はいりょ）", "jlpt": "N1", "meaning": "consideration, forethought", "example": "初めて日本に来た留学生に対して、温かい配慮を忘れない。"}
    ],
    "culture-shock-ice-water-hospitality-in-winter-vs-hot-water-culture": [
        {"word": "お冷（おひや）", "jlpt": "N2", "meaning": "cold drinking water", "example": "日本の飲食店に入ると、真冬でも冷たいお冷が無料で出される。"},
        {"word": "もてなし（もてなし）", "jlpt": "N1", "meaning": "hospitality, reception", "example": "訪れた客に対して、温かいもてなしの心で接する。"},
        {"word": "習慣（しゅうかん）", "jlpt": "N4", "meaning": "habit, custom", "example": "食事の前に「いただきます」と言うのが日本の伝統的な習慣です。"}
    ],
    "culture-shock-sleeping-on-the-train-japan-safety-and-inemuri-culture": [
        {"word": "居眠り（いねむり）", "jlpt": "N2", "meaning": "dozing off, nodding off", "example": "満員電車の中で立ったまま居眠りをしている乗客を見かけた。"},
        {"word": "治安（ちあん）", "jlpt": "N2", "meaning": "public safety, public order", "example": "日本は夜間に一人で歩いても安全なほど治安が良い。"},
        {"word": "貴重品（きちょうひん）", "jlpt": "N2", "meaning": "valuables", "example": "カフェを離れるときは、必ず財布などの貴重品を持ち歩く。"}
    ],
    "kotoba-no-aya-how-to-distinguish-yes-and-no-in-iidesu": [
        {"word": "遠慮（えんりょ）", "jlpt": "N3", "meaning": "reservation, restraint", "example": "「お茶のおかわりはいかがですか」と勧められたが、遠慮しておいた。"},
        {"word": "肯定（こうてい）", "jlpt": "N1", "meaning": "affirmation, positive", "example": "相手の提案を肯定するときは、明るい表情で返事をする。"},
        {"word": "否定（ひてい）", "jlpt": "N2", "meaning": "denial, negation", "example": "手を軽く横に振ることで、相手の申し出をやんわりと否定した。"}
    ],
    "kotoba-no-aya-how-to-use-the-final-particle-yone-for-smooth-conversation": [
        {"word": "確認（かくにん）", "jlpt": "N3", "meaning": "confirmation, verification", "example": "明日の待ち合わせ時間と場所をもう一度メールで確認する。"},
        {"word": "共有（きょうゆう）", "jlpt": "N1", "meaning": "sharing", "example": "プロジェクトの進捗状況をチーム全体でリアルタイムに共有する。"},
        {"word": "会話（かいわ）", "jlpt": "N4", "meaning": "conversation", "example": "語学を上達させる一番の近道は、毎日少しでも日本語で会話することだ。"}
    ],
    "japanese-comparing-wakaru-and-shiru-differences-in-understanding-and-knowing": [
        {"word": "理解（りかい）", "jlpt": "N3", "meaning": "understanding, comprehension", "example": "先生の説明をしっかり聞いて、文法のルールを正しく理解した。"},
        {"word": "知識（ちしき）", "jlpt": "N3", "meaning": "knowledge, information", "example": "本をたくさん読んで、幅広い分野の知識を身につけたい。"},
        {"word": "経験（けいけん）", "jlpt": "N4", "meaning": "experience", "example": "日本でアルバイトをした経験が、今の仕事にとても役立っている。"}
    ],
    "culture-shock-carb-on-carb-combos-in-japan-ramen-fried-rice-gyoza-rice-vermicelli": [
        {"word": "炭水化物（たんすいかぶつ）", "jlpt": "N1", "meaning": "carbohydrate", "example": "ラーメンとチャーハンのセットは、炭水化物同士の組み合わせだ。"},
        {"word": "満腹（まんぷく）", "jlpt": "N2", "meaning": "full stomach", "example": "安くてボリューム満点の定食を食べて、お腹がいっぱい満腹になった。"},
        {"word": "組み合わせ（くみあわせ）", "jlpt": "N2", "meaning": "combination", "example": "餃子と白ご飯の組み合わせは、日本の定食屋で大人気です。"}
    ],
    "culture-shock-cash-on-delivery-refused-tip-keep-the-change": [
        {"word": "代引き（だいびき）", "jlpt": "N2", "meaning": "cash on delivery", "example": "ネット通販で注文した商品を、配達員にお金を払って代引きで受け取った。"},
        {"word": "お釣り（おつり）", "jlpt": "N3", "meaning": "change (money)", "example": "小銭がなかったので千円札を出し、レジでお釣りをもらった。"},
        {"word": "心付け（こころづけ）", "jlpt": "N1", "meaning": "tip, gratuity", "example": "日本にはチップの習慣がないため、タクシーでお釣りの心付けを断られた。"}
    ],
    "culture-shock-haircut-price-5000-yen-vs-1000-yen-cut-hong-kong-comparison": [
        {"word": "美容院（びよういん）", "jlpt": "N3", "meaning": "beauty salon, hair salon", "example": "髪が伸びてきたので、週末に駅前の美容院を予約した。"},
        {"word": "散髪（さんぱつ）", "jlpt": "N2", "meaning": "haircut", "example": "時間がないときは、10分で散髪してくれる千円カットがとても便利だ。"},
        {"word": "接客（せっきゃく）", "jlpt": "N1", "meaning": "customer service", "example": "日本の美容師さんは接客がとても丁寧で、居心地が良い。"}
    ],
    "japanese-comparing-sayonara-and-matane-differences-in-goodbye-expressions": [
        {"word": "別れ（わかれ）", "jlpt": "N3", "meaning": "parting, farewell", "example": "卒業式の日、友達と涙を流しながら別れを惜しんだ。"},
        {"word": "再会（さいかい）", "jlpt": "N1", "meaning": "reunion, meeting again", "example": "「またね」と笑顔で手を振り、次回の再会を約束した。"},
        {"word": "挨拶（あいさつ）", "jlpt": "N4", "meaning": "greeting", "example": "朝起きたら、家族や近所の人に元気よく挨拶を交わす。"}
    ],
    "kotoba-no-aya-the-trap-of-daijoubu-yes-or-no-japanese-magic-phrase": [
        {"word": "曖昧（あいまい）", "jlpt": "N2", "meaning": "ambiguous, vague", "example": "「大丈夫」という言葉は、文脈によって意味が曖昧になりやすい。"},
        {"word": "肯定（こうてい）", "jlpt": "N1", "meaning": "affirmation", "example": "レジ袋が必要かどうか聞かれて、不要なら「いりません」と明確に答える。"},
        {"word": "気遣い（きづかい）", "jlpt": "N2", "meaning": "consideration, concern", "example": "転んだ同僚に「大丈夫ですか」と声をかけ、相手を気遣う。"}
    ],
    "street-japanese-convenience-store-register-survival-guide": [
        {"word": "レジ袋（レジぶくろ）", "jlpt": "N3", "meaning": "plastic shopping bag", "example": "エコバッグを持ってきたので、「レジ袋は結構です」と断った。"},
        {"word": "温め（あたため）", "jlpt": "N3", "meaning": "heating up (food)", "example": "コンビニでお弁当を買ったら、店員さんに「温めますか」と聞かれた。"},
        {"word": "会計（かいけい）", "jlpt": "N3", "meaning": "payment, bill", "example": "スマホのバーコード決済を提示して、スムーズに会計を済ませた。"}
    ],
    "street-japanese-hair-salon-survival-shampoo-trap-guide": [
        {"word": "痒い（かゆい）", "jlpt": "N3", "meaning": "itchy", "example": "シャンプーのときに「痒いところはありませんか」と尋ねられた。"},
        {"word": "流す（ながす）", "jlpt": "N3", "meaning": "to rinse, to wash away", "example": "泡が髪に残らないように、シャワーのお湯でしっかり流す。"},
        {"word": "指名（しめい）", "jlpt": "N1", "meaning": "nomination, designation", "example": "いつも丁寧にカットしてくれるお気に入りの美容師さんを指名する。"}
    ],
    "culture-shock-cars-stop-when-you-raise-your-hand-pedestrian-crosswalk-in-japan": [
        {"word": "横断歩道（おうだんほどう）", "jlpt": "N3", "meaning": "pedestrian crossing", "example": "小学生が手を挙げると、横断歩道の手前で車がピタッと止まった。"},
        {"word": "一時停止（いちじていし）", "jlpt": "N2", "meaning": "temporary stop", "example": "見通しの悪い交差点では、標識に従って必ず一時停止する。"},
        {"word": "優先（ゆうせん）", "jlpt": "N2", "meaning": "priority, preference", "example": "日本の交通ルールでは、歩行者が車よりも常に優先されます。"}
    ],
    "culture-shock-japanese-first-graders-walk-to-school-alone-safety-and-independence": [
        {"word": "通学（つうがく）", "jlpt": "N3", "meaning": "commuting to school", "example": "日本の小学生は、重いランドセルを背負って一人で通学する。"},
        {"word": "自立（じりつ）", "jlpt": "N1", "meaning": "independence, self-reliance", "example": "幼い頃から自分の荷物を自分で持つことで、自立心が育つ。"},
        {"word": "集団（しゅうだん）", "jlpt": "N3", "meaning": "group, mass", "example": "安全のために、近所の子供たちが集団で並んで登校している。"}
    ],
    "kotoba-no-aya-particles-zo-and-ze-anime-vs-real-life-japanese": [
        {"word": "語尾（ごび）", "jlpt": "N2", "meaning": "end of a word/sentence", "example": "アニメの主人公は、語尾に「〜ぞ」や「〜ぜ」をよく使う。"},
        {"word": "違和感（いわかん）", "jlpt": "N2", "meaning": "uncomfortable feeling, oddity", "example": "初対面の人に乱暴な言葉遣いをすると、強い違和感を与えてしまう。"},
        {"word": "現実（げんじつ）", "jlpt": "N3", "meaning": "reality, actuality", "example": "アニメの世界の日本語と、現実の日常会話の使い分けを理解する。"}
    ],
    "japanese-comparing-ageru-kureru-morau-differences-in-giving-and-receiving": [
        {"word": "授受（じゅじゅ）", "jlpt": "N1", "meaning": "giving and receiving", "example": "「あげる」「くれる」「もらう」は、物の授受を表す重要表現だ。"},
        {"word": "恩恵（おんけい）", "jlpt": "N1", "meaning": "grace, favor, blessing", "example": "先輩に親切に教えてもらった恩恵に対して、感謝の気持ちを伝える。"},
        {"word": "視点（してん）", "jlpt": "N2", "meaning": "perspective, point of view", "example": "話し手の視点が誰にあるかによって、使う動詞が変化する。"}
    ],
    "street-japanese-station-ticket-gate-dungeon-guide": [
        {"word": "改札（かいさつ）", "jlpt": "N3", "meaning": "ticket gate", "example": "交通系ICカードをタッチして、電車の改札を通過した。"},
        {"word": "精算（せいさん）", "jlpt": "N2", "meaning": "fare adjustment, settlement", "example": "チャージの残高が足りなかったので、精算機で百円を入金した。"},
        {"word": "乗り換え（のりかえ）", "jlpt": "N3", "meaning": "transfer (trains)", "example": "新宿駅は路線が多くて複雑なので、乗り換えに十分な時間を取る。"}
    ],
    "street-japanese-izakaya-survival-guide": [
        {"word": "お通し（おとおし）", "jlpt": "N2", "meaning": "appetizer served at izakaya", "example": "居酒屋で席に座ると、注文する前に小鉢のお通しが運ばれてきた。"},
        {"word": "乾杯（かんぱい）", "jlpt": "N4", "meaning": "toast, cheers", "example": "ビールが全員に行き渡ったところで、元気に「乾杯！」と声を合わせた。"},
        {"word": "とりあえず（とりあえず）", "jlpt": "N3", "meaning": "for now, first of all", "example": "席に着いたら、まずは「とりあえず生ビールを二つ」と頼むのが定番だ。"}
    ],
    "japanese-comparing-zenzen-and-mattaku-differences-in-degree-and-nuance": [
        {"word": "全然（ぜんぜん）", "jlpt": "N4", "meaning": "not at all (colloquial: completely)", "example": "昨日ぐっすり眠ったので、今日は全然疲れていません。"},
        {"word": "全く（まったく）", "jlpt": "N3", "meaning": "entirely, completely", "example": "初めて聞く専門用語ばかりで、話の内容が全く分からなかった。"},
        {"word": "否定（ひてい）", "jlpt": "N2", "meaning": "negation, denial", "example": "「全然」「全く」のどちらも、後ろに否定の言葉が続くのが本来の形です。"}
    ],
    "kotoba-no-aya-the-seven-faces-of-sumimasen-apology-thanks-call": [
        {"word": "謝罪（しゃざい）", "jlpt": "N1", "meaning": "apology", "example": "相手の足を踏んでしまったときは、すぐに「すみません」と謝罪する。"},
        {"word": "感謝（かんしゃ）", "jlpt": "N3", "meaning": "thanks, gratitude", "example": "落としたハンカチを拾ってくれた親切な人に、「すみません」とお礼を言った。"},
        {"word": "呼びかけ（よびかけ）", "jlpt": "N2", "meaning": "calling out, excuse me", "example": "居酒屋で忙しそうな店員さんを呼ぶときは、「すみません」と呼びかける。"}
    ],
    "kotoba-no-aya-sonosetsu-wa-doumo-thanks-and-apology": [
        {"word": "先日（せんじつ）", "jlpt": "N3", "meaning": "the other day, recently", "example": "先日は大変お世話になり、心よりお礼申し上げます。"},
        {"word": "挨拶（あいさつ）", "jlpt": "N4", "meaning": "greeting", "example": "久しぶりに会った取引先の担当者に「その節はどうも」と挨拶した。"},
        {"word": "感謝（かんしゃ）", "jlpt": "N3", "meaning": "gratitude", "example": "過去に助けてもらった親切への感謝を、改めて言葉にして伝える。"}
    ],
    "street-japanese-cafe-order-survival-mug-or-paper-guide": [
        {"word": "店内（てんない）", "jlpt": "N3", "meaning": "inside the shop", "example": "「店内でお召し上がりですか、それともお持ち帰りですか」と聞かれた。"},
        {"word": "持ち帰り（もちかえり）", "jlpt": "N3", "meaning": "takeout, to go", "example": "時間がないので、ホットコーヒーを紙コップで持ち帰りにした。"},
        {"word": "注文（ちゅうもん）", "jlpt": "N3", "meaning": "order", "example": "カウンターで自分の好みのサイズとミルクの種類を指定して注文する。"}
    ],
    "culture-shock-why-japanese-streets-are-clean-without-trash-cans": [
        {"word": "ゴミ箱（ごみばこ）", "jlpt": "N4", "meaning": "trash can, rubbish bin", "example": "日本の街中にはゴミ箱が少ないため、ゴミは家に持ち帰るのがマナーだ。"},
        {"word": "分別（ぶんべつ）", "jlpt": "N2", "meaning": "sorting, separation (garbage)", "example": "燃えるゴミとプラスチックを正しく分別して指定の日に出す。"},
        {"word": "美化（びか）", "jlpt": "N1", "meaning": "beautification", "example": "住民が交代で道路を掃除することで、街の美化が保たれている。"}
    ],
    "japanese-comparing-chotto-and-sukoshi-differences": [
        {"word": "少々（しょうしょう）", "jlpt": "N3", "meaning": "a little, just a minute", "example": "「確認いたしますので、少々お待ちください」と丁寧に案内された。"},
        {"word": "遠慮（えんりょ）", "jlpt": "N3", "meaning": "hesitation, declining", "example": "飲み会に誘われたが、明日は朝が早いので「ちょっと…」と遠慮した。"},
        {"word": "程度（ていど）", "jlpt": "N3", "meaning": "degree, amount", "example": "「少し」は客観的な量を表し、「ちょっと」は話し言葉でよく使われる。"}
    ],
    "street-japanese-onsen-sento-bath-rules-survival-guide": [
        {"word": "温泉（おんせん）", "jlpt": "N2", "meaning": "hot spring", "example": "旅行で箱根の温泉に行き、露天風呂でゆっくりと疲れを癒やした。"},
        {"word": "湯船（ゆぶね）", "jlpt": "N2", "meaning": "bathtub", "example": "体を石鹸で洗ってから湯船に入るのが、日本の温泉の基本マナーです。"},
        {"word": "脱衣所（だついじょ）", "jlpt": "N2", "meaning": "dressing room, locker room", "example": "お風呂から上がる前に、脱衣所の手前で体をタオルでよく拭く。"}
    ],
    "kotoba-no-aya-the-trap-of-tekitou-proper-or-careless": [
        {"word": "適当（てきとう）", "jlpt": "N4", "meaning": "suitable / careless, random", "example": "野菜を適当な大きさに切って、鍋に入れて煮込みます。"},
        {"word": "いい加減（いいかげん）", "jlpt": "N3", "meaning": "careless, irresponsible", "example": "約束の時間を守らないようないい加減な態度は、信用を失ってしまう。"},
        {"word": "適切（てきせつ）", "jlpt": "N3", "meaning": "appropriate, adequate", "example": "状況に応じて、最も適切で丁寧な言葉遣いを選ぶことが大切だ。"}
    ],
    "culture-shock-why-japanese-toilets-play-water-sounds-otohime": [
        {"word": "消音（しょうおん）", "jlpt": "N1", "meaning": "muting, sound suppression", "example": "トイレの音を周囲に聞かれないように、音姫のボタンを押して消音する。"},
        {"word": "羞恥心（しゅうちしん）", "jlpt": "N1", "meaning": "sense of shame, bashfulness", "example": "他人に流水音を聞かれるのが恥ずかしいという羞恥心から開発された。"},
        {"word": "節水（せっすい）", "jlpt": "N1", "meaning": "saving water, water conservation", "example": "何度も水を流す無駄をなくすため、音姫は大きな節水効果を発揮する。"}
    ],
    "kotoba-no-aya-tsumaranai-mono-gift-giving-psychology": [
        {"word": "謙遜（けんそん）", "jlpt": "N2", "meaning": "modesty, humility", "example": "自分の成果を誇らず、控えめに話すのが日本の伝統的な謙遜の文化だ。"},
        {"word": "贈り物（おくりもの）", "jlpt": "N3", "meaning": "gift, present", "example": "お世話になった先生へ、「つまらないものですが」と感謝の贈り物を渡した。"},
        {"word": "心配り（こころくばり）", "jlpt": "N1", "meaning": "thoughtfulness, consideration", "example": "相手の好みをあらかじめリサーチして手土産を選ぶ優しい心配り。"}
    ],
    "japanese-comparing-tabun-osoraku-kitto-differences": [
        {"word": "多分（たぶん）", "jlpt": "N4", "meaning": "probably, perhaps", "example": "空が少し曇ってきたので、多分夜には雨が降るでしょう。"},
        {"word": "恐らく（おそらく）", "jlpt": "N3", "meaning": "probably, likely (formal)", "example": "交通渋滞が発生しているため、恐らく電車の到着は遅れる見込みです。"},
        {"word": "きっと（きっと）", "jlpt": "N4", "meaning": "surely, definitely", "example": "これだけ真剣に勉強したのだから、明日のJLPT試験はきっと合格できます。"}
    ],
    "street-japanese-rainy-day-umbrella-stand-dungeon-guide": [
        {"word": "傘立て（かさたて）", "jlpt": "N3", "meaning": "umbrella stand", "example": "店頭の傘立てに鍵付きの番号札があったので、施錠して預けた。"},
        {"word": "ビニール袋（ビニールぶくろ）", "jlpt": "N3", "meaning": "plastic bag", "example": "雨の日はお店の入口で、濡れた傘を入れる細長いビニール袋をもらう。"},
        {"word": "盗難（とうなん）", "jlpt": "N2", "meaning": "theft", "example": "ビニール傘の取り違えや盗難を防ぐため、目印のシールを貼っておく。"}
    ],
    "culture-shock-leaving-smartphone-unattended-cafe-japan": [
        {"word": "席取り（せきとり）", "jlpt": "N2", "meaning": "securing a seat", "example": "カフェで注文する前に、テーブルにハンカチを置いて席取りをした。"},
        {"word": "治安（ちあん）", "jlpt": "N2", "meaning": "public safety, security", "example": "財布やスマホを机に置いたまま離れても盗まれないほど、日本の治安は良い。"},
        {"word": "油断（ゆだん）", "jlpt": "N2", "meaning": "carelessness, inattention", "example": "いくら安全な街でも、海外旅行のときは決して油断してはいけない。"}
    ],
    "street-japanese-kaitenzushi-hot-water-express-lane-survival-guide": [
        {"word": "蛇口（じゃぐち）", "jlpt": "N2", "meaning": "faucet, tap", "example": "席にある給茶用の蛇口に湯飲みを押し当てて、熱いお茶を淹れる。"},
        {"word": "特急（とっきゅう）", "jlpt": "N4", "meaning": "express lane / express train", "example": "タッチパネルで注文した寿司が、特急レーンに乗って席まで素早く届いた。"},
        {"word": "お会計（おかいけい）", "jlpt": "N3", "meaning": "check, bill", "example": "食べ終わった後、店員さんを呼んでお皿の枚数を数えてもらいお会計へ向かう。"}
    ],
    "japanese-comparing-futoru-futotteiru-aspect-differences": [
        {"word": "太る（ふとる）", "jlpt": "N4", "meaning": "to gain weight (action)", "example": "毎晩甘い夜食を食べていたら、一ヶ月で二キロも太ってしまった。"},
        {"word": "太っている（ふとっている）", "jlpt": "N4", "meaning": "to be plump (state)", "example": "あの公園にいる猫は、近所の人からご飯をもらって丸々と太っている。"},
        {"word": "状態（じょうたい）", "jlpt": "N3", "meaning": "condition, state", "example": "薬を飲んで安静にしていたおかげで、熱も下がって健康な状態に戻った。"}
    ],
    "street-japanese-ramen-ticket-machine-call-survival-guide": [
        {"word": "食券（しょっけん）", "jlpt": "N3", "meaning": "meal ticket", "example": "お店の入口にある自動券売機で、ラーメンと味玉の食券を購入した。"},
        {"word": "好み（このみ）", "jlpt": "N3", "meaning": "preference, taste", "example": "ラーメンの食券を店員に渡す際、「麺硬め、味濃いめ」と好みを伝えた。"},
        {"word": "コール（コール）", "jlpt": "N2", "meaning": "ordering call/phrase", "example": "二郎系ラーメンの独特なコールに最初は緊張したが、無事に注文できた。"}
    ],
    "kotoba-no-aya-otsukaresama-vs-gokurousama-trap": [
        {"word": "お疲れ様（おつかれさま）", "jlpt": "N3", "meaning": "thank you for your hard work", "example": "先輩や上司に対して仕事を終えたときは、「お疲れ様でした」と声をかける。"},
        {"word": "ご苦労様（ごくろうさま）", "jlpt": "N3", "meaning": "good job (to subordinates)", "example": "社長が部下の労をねぎらう際に「ご苦労様」と言葉をかけた。"},
        {"word": "目上（めうえ）", "jlpt": "N3", "meaning": "superior, senior", "example": "日本のビジネス社会では、目上の人に対する敬語の使い分けがとても大切だ。"}
    ],
    "culture-shock-why-no-phone-calls-and-newspapers-on-japanese-trains": [
        {"word": "マナーモード（マナーモード）", "jlpt": "N3", "meaning": "silent mode (phone)", "example": "電車に乗る前に、スマートフォンの着信音を消してマナーモードに設定する。"},
        {"word": "配慮（はいりょ）", "jlpt": "N1", "meaning": "consideration, concern", "example": "静かな車内空間を守るため、大声での会話や通話を控える配慮が求められる。"},
        {"word": "沈黙（ちんもく）", "jlpt": "N1", "meaning": "silence", "example": "朝の通勤電車は乗客の沈黙が守られており、とても落ち着いた雰囲気だ。"}
    ],
    "japanese-comparing-iku-vs-kuru-perspective-trap": [
        {"word": "行く（いく）", "jlpt": "N5", "meaning": "to go", "example": "友達が待っているカフェへ、今から自転車で行きます。"},
        {"word": "来る（くる）", "jlpt": "N5", "meaning": "to come", "example": "日本語では、自分が相手の家へ向かうときも「今から行きます」と表現する。"},
        {"word": "視点（してん）", "jlpt": "N2", "meaning": "point of view, perspective", "example": "話し手と聞き手のどちらの視点から空間を捉えるかが重要になる。"}
    ],
    "street-japanese-delivery-redelivery-undelivered-notice-dungeon-guide": [
        {"word": "不在票（ふざいひょう）", "jlpt": "N2", "meaning": "delivery notice", "example": "留守中に荷物が届いたようで、ポストに不在票が入っていた。"},
        {"word": "再配達（さいはいたつ）", "jlpt": "N2", "meaning": "redelivery", "example": "不在票のQRコードをスマホで読み取り、今夜の再配達を申し込んだ。"},
        {"word": "追跡（ついせき）", "jlpt": "N1", "meaning": "tracking", "example": "荷物の問い合わせ番号をネットに入力して、配送状況を追跡する。"}
    ],
    "kotoba-no-aya-the-trap-of-kekkoudesu-yes-or-no": [
        {"word": "結構です（けっこうです）", "jlpt": "N3", "meaning": "no thank you / that's fine", "example": "「レジ袋をお付けしますか」と聞かれ、手を軽く振って「結構です」と断った。"},
        {"word": "承諾（しょうだく）", "jlpt": "N1", "meaning": "consent, agreement", "example": "企画の変更を上司に相談したところ、快く承諾してもらえた。"},
        {"word": "辞退（じたい）", "jlpt": "N1", "meaning": "declining, refusal", "example": "せっかく推薦をいただいたが、今回は都合により辞退することにした。"}
    ],
    "culture-shock-hanko-seal-stamp-culture-and-signature": [
        {"word": "印鑑（いんかん）", "jlpt": "N1", "meaning": "personal seal, stamp", "example": "銀行で新しい口座を開設するため、持参した印鑑を押印した。"},
        {"word": "押印（おういん）", "jlpt": "N1", "meaning": "affixing a seal", "example": "契約書の内容をしっかり確認した上で、署名と押印を行った。"},
        {"word": "署名（しょめい）", "jlpt": "N2", "meaning": "signature", "example": "クレジットカード決済のレシートに、漢字で丁寧に署名した。"}
    ],
    "street-japanese-clinic-medical-questionnaire-pharmacy-guide": [
        {"word": "問診票（もんしんひょう）", "jlpt": "N2", "meaning": "medical questionnaire", "example": "病院の受付で問診票を渡され、現在の症状やアレルギーの有無を記入した。"},
        {"word": "保険証（ほけんしょう）", "jlpt": "N2", "meaning": "health insurance card", "example": "クリニックにかかるときは、忘れずに健康保険証を受付へ提示する。"},
        {"word": "お薬手帳（おくすりてちょう）", "jlpt": "N2", "meaning": "medication notebook", "example": "過去に処方された薬の重複を防ぐため、薬局でお薬手帳を見せた。"}
    ],
    "japanese-comparing-hazu-vs-wake-nuance-differences": [
        {"word": "はず（はず）", "jlpt": "N3", "meaning": "should be, expected to", "example": "念入りに準備を整えたので、明日のプレゼンはうまくいくはずです。"},
        {"word": "わけ（わけ）", "jlpt": "N3", "meaning": "reason, naturally so", "example": "毎日三時間も日本語を特訓しているのだから、上達が早いわけだ。"},
        {"word": "納得（なっとく）", "jlpt": "N3", "meaning": "convinced, understanding", "example": "先輩の丁寧な解説を聞いて、複雑なルールの理由がようやく納得できた。"}
    ],
    "culture-shock-shoumi-kigen-vs-shouhi-kigen-discount-stickers": [
        {"word": "賞味期限（しょうみきげん）", "jlpt": "N3", "meaning": "best-before date", "example": "賞味期限はおいしく食べられる目安なので、一日過ぎてもすぐに傷むわけではない。"},
        {"word": "消費期限（しょうひきげん）", "jlpt": "N3", "meaning": "expiration date", "example": "サンドイッチやお刺身などの生ものは、消費期限内に食べる必要があります。"},
        {"word": "見切り品（みきりひん）", "jlpt": "N2", "meaning": "discounted items near expiry", "example": "夕方のスーパーで見切り品に貼られた半額シールを見つけて嬉しくなった。"}
    ],
    "kotoba-no-aya-is-shouchidesu-wrong-business-japanese-trap": [
        {"word": "承知（しょうち）", "jlpt": "N2", "meaning": "acknowledging, consent", "example": "上司からの指示に対して、「承知いたしました。すぐに対応します」と返事をした。"},
        {"word": "了解（りょうかい）", "jlpt": "N3", "meaning": "understanding, roger", "example": "同僚同士のチャット連絡では「了解です」と返信することが多い。"},
        {"word": "謙譲語（けんじょうご）", "jlpt": "N1", "meaning": "humble language", "example": "取引先のクライアントに対しては、敬意を込めて謙譲語を使うのがビジネスマナーだ。"}
    ],
    "street-japanese-city-hall-resident-registration-dungeon-guide": [
        {"word": "転入届（てんにゅうとどけ）", "jlpt": "N3", "meaning": "notice of moving in", "example": "新しい街に引っ越してきたので、十四日以内に市役所へ転入届を提出する。"},
        {"word": "窓口（まどぐち）", "jlpt": "N3", "meaning": "service counter, window", "example": "番号札を取ってロビーの椅子で待ち、自分の番号が呼ばれたら市民課の窓口へ向かう。"},
        {"word": "住民票（じゅうみんひょう）", "jlpt": "N2", "meaning": "certificate of residence", "example": "銀行口座の開設や就職手続きで必要になるため、市役所で住民票の写しを取得した。"}
    ],
    "japanese-comparing-rashii-souda-youda-differences": [
        {"word": "らしい（らしい）", "jlpt": "N3", "meaning": "seems like, I hear that", "example": "天気予報によると、明日は午後から激しい雨が降るらしいです。"},
        {"word": "そうだ（そうだ）", "jlpt": "N3", "meaning": "looks like (appearance)", "example": "空に真っ黒な雨雲が広がってきて、今にも雨が降りそうだ。"},
        {"word": "ようだ（ようだ）", "jlpt": "N3", "meaning": "seems like (sensory inference)", "example": "外を歩く人たちがみんな傘を差しているところを見ると、雨が降っているようだ。"}
    ]
}

def generate_vocab_box_html(items, lead="この学習ノートに登場した、覚えておきたい重要日本語："):
    cards_html = []
    for it in items:
        badge_cls = f"c-badge--jlpt-{it['jlpt'].lower()}"
        card = f"""    <div class="c-vocab-card">
      <div class="c-vocab-card__header">
        <span class="c-vocab-card__word">{it['word']}</span>
        <span class="c-badge c-badge--jlpt {badge_cls}">JLPT {it['jlpt']}</span>
      </div>
      <p class="c-vocab-card__meaning"><strong>意味：</strong>{it['meaning']}</p>
      <p class="c-vocab-card__example"><strong>例文：</strong>{it['example']}</p>
    </div>"""
        cards_html.append(card)

    cards_joined = "\n".join(cards_html)
    return f"""<div class="c-vocab-box">
  <h3 class="c-vocab-box__title">🎯 今回の語彙（重要ボキャブラリー）</h3>
  <p class="c-vocab-box__lead">{lead}</p>
  <div class="c-vocab-grid">
{cards_joined}
  </div>
</div>"""

def generate_vocab_markdown(items, lead="この学習ノートに登場した、覚えておきたい重要日本語："):
    lines = [
        "## 🎯 今回の語彙（重要ボキャブラリー）\n",
        f"{lead}\n"
    ]
    for it in items:
        lines.append(f"* **{it['word']}** 【JLPT {it['jlpt']}】")
        lines.append(f"  * 意味：{it['meaning']}")
        lines.append(f"  * 例文：{it['example']}")
    return "\n".join(lines) + "\n"

# 1. Update Markdown files
updated_md = 0
for md in glob.glob('content/posts/*.md'):
    fname = os.path.basename(md)
    slug = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', fname).replace('.md', '')
    if slug in VOCAB_MASTER:
        items = VOCAB_MASTER[slug]
        new_md_sec = generate_vocab_markdown(items)
        with open(md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace existing vocab section
        pat = r'##\s*🎯?\s*.*?(?:語彙|ボキャブラリー).*?\n.*?(?=\n---|\Z)'
        if re.search(pat, content, re.DOTALL):
            new_content = re.sub(pat, new_md_sec.strip(), content, flags=re.DOTALL)
            if new_content != content:
                with open(md, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                updated_md += 1

print(f"Updated {updated_md} Markdown files with master vocab & clean examples.")

slug_to_box_html = {}
for slug, items in VOCAB_MASTER.items():
    slug_to_box_html[slug] = generate_vocab_box_html(items)

# Add slug aliases for posts whose WordPress post_name differs from markdown filename
aliases = {
    "kotoba-no-aya-sonosetsu-wa-doumo": "kotoba-no-aya-sonosetsu-wa-doumo-thanks-and-apology",
    "kotoba-no-aya-the-seven-faces-of-sumimasen": "kotoba-no-aya-the-seven-faces-of-sumimasen-apology-thanks-call",
    "japanese-comparing-zenzen-and-mattaku-differences": "japanese-comparing-zenzen-and-mattaku-differences-in-degree-and-nuance"
}
for short_slug, full_slug in aliases.items():
    if full_slug in slug_to_box_html:
        slug_to_box_html[short_slug] = slug_to_box_html[full_slug]

with open('clean_master_vocab_boxes.json', 'w', encoding='utf-8') as f:
    json.dump(slug_to_box_html, f, ensure_ascii=False, indent=2)

print("Saved clean_master_vocab_boxes.json with aliases.")
