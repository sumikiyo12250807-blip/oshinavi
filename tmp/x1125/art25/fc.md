# 11/25 記事3本の独立ファクトチェック

調べ方：記事を1文ずつ、公式・売り場のページを取り直して照合した（取得したページは同じフォルダの fc_*.txt）。「」の引用は fc_check.py で生の文字と機械照合した（結果は fc_check_out.txt）。曜日はすべて暦で確認し、全部合っていた。枚方の会場ページは Claude in Chrome で開いて、ページ上で文字一致を確かめた。

件数：🔴 0／🟠 1／🟡 6（ほかに登録の食い違い2件）

---

## 1. 春の謡会2027（harunoutaikai.md）

🔴・🟠・🟡 なし。

照合できた点：
- 主催、「うたう（謡う）」、府の発表の引用2つ、登録有形文化財、ねらい（若い世代）は府・市の発表と一致
- 2026年の回（2/22・2/23、俊寛・大会、出演4組）は市の発表と一致
- 出演・ナビゲーター（FM802）・開場/開演/終演・4,000円・席3種と見え方・柱の注意は特設サイトと FANY で一致
- 1/30 の音楽3人（かやゆーを含む）は特設サイトと FANY で一致（10/16 の府・市の発表には、かやゆーの名前がまだない）
- 二人静のあらすじと季節（観世 1月／金春 正月／金剛 早春）は能楽協会の曲目データベースと一致
- 紅葉狩のあらすじと引用は the能ドットコムと一致
- 谷町四丁目10号出口・谷町六丁目7号出口から各徒歩5分は能楽堂の公式と一致
- FANY の一般発売（11/28(土) 10:00〜、1/30分は1/28(木) 23:59まで、1/31分は1/29(金) 23:59まで）、1人1公演1席種4枚まで、当日券の注意も一致
- 特設サイトのプレイガイドには e+・ローソンチケット・ぴあ・FANY・CN が並ぶ。記事は e+ とぴあだけを挙げているが、誤りではない

根拠：
https://www.pref.osaka.lg.jp/hodo/fumin/o070100/prs_51281.html
https://www.city.osaka.lg.jp/hodoshiryo/keizaisenryaku/0000687300.html
https://www.city.osaka.lg.jp/hodoshiryo/keizaisenryaku/0000668042.html
https://osaka-ca-fes.jp/project/event/harunoutakai2027/
https://ticket.fany.lol/event/detail/22062
https://ticket.fany.lol/reception/71103/56006
https://ticket.fany.lol/reception/71103/56007
https://www.nohgaku.or.jp/encyclopedia/program_db/futarishizuka
https://www.the-noh.com/jp/plays/data/program_014.html
https://noh-kyogen.com/access/

---

## 2. Kids meet Jazz! with May J.（mayj_kidsjazz.md）

🟡 「子ども（中学生以下）は1,500円」
→ 会場のページは「子ども（3歳以上、中学生以下）：1,500 円」。3歳未満は保護者1名につき1名までひざ上なら無料。今のままだと「0〜2歳も1,500円」と読める。年齢の条件を書かない決まりと合わせて、どう書くかを決めてほしい。
https://hirakata-arts.jp/event/detail_73404.html

照合できた点：
- e+ の引用3つ（のべ20万人／夢のコラボ／多くの人に感動）、テーマ、初登場は e+ と一致
- 会場ページの引用2つ（英語やダンス／楽しさ満載＆親子で感動）は Chrome で開いたページの文字と一致
- 出演、演奏予定曲4曲（並びは会場ページと同じ）、内容変更・駐車場の注意は会場ページと一致
- 開場14:15・開演15:00、大人3,500円は会場ページと一致
- e+ の先着一般発売（11/26(木)10:00〜2/27(土)18:00）は e+ と一致
- 会場の電話/WEB は11/26、窓口は11/27(金)で残席がある場合のみ、会員先行は11/14(土)。いずれも会場ページと一致
- 会場ページには、ぴあ・ローソンチケット・e+ が並ぶ

根拠：
https://eplus.jp/sf/detail/4620750001-P0030001P021001
https://hirakata-arts.jp/event/detail_73404.html

---

## 3. 土岐麻子 Sentimental Journey Yokosuka Bayside Breeze vol.8（tokiasako.md）

🟠 「公式サイトも、一般発売を「11月29日（日）10:00〜」と案内しているの」
→ 劇場サイトの文字は「一般発売 2026年11月29日（日）」だけで、時刻が書かれていない。「10:00〜」はチラシの画像（PDF）にしかなく、表記も「2026年11月29日(日)10:00〜」（半角かっこ）。この引用は生の文字と一致しない。「劇場のチラシも、一般発売を11/29(日) 10:00〜と案内している」のように「」を外すか、サイトの文字どおりに直してほしい。なお劇場サイトには「プレミアム倶楽部 会員発売 2026年11月28日（土）」もある。
https://www.yokosuka-arts.or.jp/performance/calendar/detail.php?id=3675
https://www.yokosuka-arts.or.jp/performance/ticket/index.php
https://www.yokosuka-arts.or.jp/contents/storage/images/event/2026/3675/3.pdf

🟡 これまでの顔ぶれ（Vol.1〜Vol.6）のあと「そこへ、vol.8として土岐麻子が登場するの」
→ シリーズのページには「今後の公演」として「12月27日（日）Vol.7 日食なつこ「エウロパ」」が載っている。Vol.7 に触れないと、Vol.6 の次が Vol.8 のように読める。
https://www.yokosuka-arts.or.jp/project/bayside-breeze/

🟡 見出しと1文目の「…Yokosuka Bayside Breeze vol.8」
→ e+・劇場・チラシはどれも「Vol.8」（V が大文字）。OSHINAVI の登録名が vol.8 なので、そろえるかどうか決めてほしい。
https://eplus.jp/sf/detail/0144000006-P0030149P021001

🟡 「劇場会員（プレミアム俱楽部）」
→ 記事の字は「俱」（U+4FF1）。劇場は「倶」（U+5036）を使っている。
https://www.yokosuka-arts.or.jp/performance/calendar/detail.php?id=3675

🟡 「学生券は2,750円、劇場会員（プレミアム俱楽部）は4,950円」
→ 金額は正しい。ただし、この金額そのものはどこにも書かれていない。チラシにあるのは「学生券（24歳までの学生）は一般料金の半額」「劇場プレミアム倶楽部会員は10%OFF」で、そこから計算した値。劇場サイトにも 5,500円とマークしか出ていない。
https://www.yokosuka-arts.or.jp/contents/storage/images/event/2026/3675/3.pdf

🟡 「同じ5月には、北京、上海、深センをまわる中国ツアーも…開かれたのよ」
→ Billboard JAPAN の記事は開催の告知（「開催する」）で、実際に開かれたことまでは書かれていない。日程は 5/15 北京・5/16 上海・5/17 深セン で記事と一致。
https://www.billboard-japan.com/d_news/detail/148386/2

照合できた点：
- シリーズの紹介（2024年から・引用2つ・小劇場）と Vol.1〜Vol.6 の中身は劇場のシリーズページと一致
- 出演3人と開場15:15・開演16:00は e+ と劇場で一致
- 汐入徒歩約1分、横須賀徒歩約8分、入口はベイスクエアよこすか1番館4階は劇場のアクセスページと一致
- 全席指定5,500円は劇場とチラシで一致
- e+ の先着一般発売（11/29(日)10:00〜2/18(木)18:00）、座席選択（11/29 10:00〜）、抽選プレオーダー（11/19(木)終了）は e+ と一致
- 2023年のツアー、BLUE NOTE TOKYO（2025/5/24）と引用、2025年6〜7月の6か所と引用は Billboard JAPAN と一致
- 劇場のプレイガイドは e+ とぴあ

根拠：
https://www.yokosuka-arts.or.jp/project/bayside-breeze/
https://www.yokosuka-arts.or.jp/information/access/
https://www.billboard-japan.com/d_news/detail/147213/2
https://www.billboard-japan.com/d_news/detail/148642/2

---

## 登録（dump.txt）との食い違い

- id 36535（春の謡会 1/30）：登録の出演者「「二人静」大槻文藏／山田将司（THE BACK HORN）」に、かやゆー（ヤングスキニー）とさとう。が入っていない。記事・FANY・特設サイトは3人。
  https://ticket.fany.lol/event/detail/22062
- id 52883（土岐麻子）：11/19 に終わった「抽選プレオーダー受付（〜11/19 23:59）」の枠が、まだ登録に残っている（今日は11/25）。
  https://eplus.jp/sf/detail/0144000006-P0030149P021001
- id 36536・45838 は、記事・登録・売り場で食い違いなし。
