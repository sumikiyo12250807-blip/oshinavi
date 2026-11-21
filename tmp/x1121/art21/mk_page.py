# -*- coding: utf-8 -*-
# 11/21 記事3本の確認ページ（本文＋出典URL）→ artcheck_1121.html（x1119/art19/mk_page.py の形）
import io
A = 'C:/Users/user/oshinavi/tmp/x1121/art21/'
s = io.open('C:/Users/user/oshinavi/tmp/x1119/art19/mk_page.py', encoding='utf-8').read()
s = s.replace("A = 'C:/Users/user/oshinavi/tmp/x1119/art19/'", "A = '%s'" % A)
s = s.replace("ARTS = [('daibakushow', 'DAIBAKUSHOW 2026'), ('asagaya', '阿佐ヶ谷姉妹 ミーツ オーケストラ'), ('plastictree', 'Plastic Tree 年末公演')]",
              "ARTS = [('montecristo', '宝塚歌劇 雪組『Monte-Cristo』東京公演'), ('watanabemisato', '渡辺美里と京フィルコンサート'), ('hitofuji', 'リーディングアクト『一富士茄子牛焦げルギー』')]")
a = s.index('NOTES = ['); b = s.index(']\n', a) + 2
s = s[:a] + '''NOTES = [
    '独立の確かめ（別の係・出典のページを全部自分で開き直した・引用は生の文字と機械で一致・曜日は暦で計算）＝🔴0🟠1🟡2 → 3つとも直したわ',
    'モンテ・クリスト：欧州ツアーの「9月から」を「2026年9月から」に（来年と読まれないように）／1/17(日) 15:30 のライブ中継・配信の段落も入れてある（いらなければ消すわ）',
    '一富士：受付の締切「回の2日前 23:59まで」は FANY の締切と分かる形に・e+ とぴあは「締切は売り場ごとに違うから、それぞれのページで確かめてね」を1行足した／開演は 1/8・1/14 が 19:00、1/15 が 15:00 の1回だけ（売り場どおり）',
    '一富士の登録の穴を直したわ＝ぴあ（東京・大阪）と e+（9回）の 11/22 10:00 一般発売が入っていなかった → ぴあ 2枠・e+ 9枠を足して、売り場と照らして一致',
    '渡辺美里：中身は曲目3曲（e+）と「宝くじ文化公演」の説明（主催の自治総合センター）が中心。字数は 1,200字ちょっと',
]
''' + s[b:]
s = s.replace('<h1>11/19 の記事3本（11/21・11/22 発売の組）</h1>', '<h1>11/21 の記事3本（11/22 発売の組）</h1>').replace('artcheck_1119.html', 'artcheck_1121.html')
assert 'artcheck_1121.html' in s and 'montecristo' in s and '11/21 の記事3本' in s
exec(compile(s, 'mk', 'exec'))
