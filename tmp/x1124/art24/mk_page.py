# -*- coding: utf-8 -*-
# 11/24 記事3本の確認ページ（本文＋出典URL）→ artcheck_1124.html（x1119/art19/mk_page.py の形）
import io
A = 'C:/Users/user/oshinavi/tmp/x1124/art24/'
s = io.open('C:/Users/user/oshinavi/tmp/x1119/art19/mk_page.py', encoding='utf-8').read()
s = s.replace("A = 'C:/Users/user/oshinavi/tmp/x1119/art19/'", "A = '%s'" % A)
s = s.replace("ARTS = [('daibakushow', 'DAIBAKUSHOW 2026'), ('asagaya', '阿佐ヶ谷姉妹 ミーツ オーケストラ'), ('plastictree', 'Plastic Tree 年末公演')]",
              "ARTS = [('amamitomochika', '天海と友近、結局飯尾 THEオーディション4'), ('uzakiryudo', '宇崎竜童 弾き語りLIVE2027'), ('nagoyaongakusai', '名古屋国際音楽祭 山田和樹×バーミンガム市響×ヒラリー・ハーン')]")
a = s.index('NOTES = ['); b = s.index(']\n', a) + 2
s = s[:a] + '''NOTES = [
    '独立の確かめ（別の係が出典のページを自分で開き直した・「」の引用43か所は元の文字と全部一致・曜日は暦で計算）＝🔴1🟠8🟡6 → 直したわ',
    '宇崎竜童：「2026年は…京都とまわってきた」は誤り（京都 11/29 はまだこれから）＝「福岡とまわってきて、11/29 には京都が控えている」に直した／今回の発売でない京都の受付（11/25 締切・残席わずか）の2行は外した／ローチケの名前は外した',
    '天海と友近：「約2時間」は公式の画面に出ていない文だったので外した／「1人4枚まで」は買い方の条件なので外した／出典を、開けなかった研音からフジテレビダイレクトの同じ文に／第3回は「開かれると伝えていた」に',
    '名古屋：U25 の注（年齢と本人確認の条件）とローソンチケットの名前は外した',
    'OSHINAVI の登録：宇崎竜童 R9年 3/21 浜松は別のカード（30589）にちゃんと載っていた／天海と友近の e+「抽選2次プレオーダー」は今夜 23:59 締切で、夜の公開より前に終わるので足していない',
    '11/23 の3本（海宝直人・小曽根真・大宮よしもと）＝ https://claude.ai/artifact/FJWyED2ZB3XDDDxYNcp7n5 と 11/21 の3本＝ https://claude.ai/artifact/Ud4539xduoPp88v14bEEAv もまだ OK 待ちよ',
]
''' + s[b:]
s = s.replace('<h1>11/19 の記事3本（11/21・11/22 発売の組）</h1>', '<h1>11/24 の記事3本（11/28 発売の組）</h1>').replace('artcheck_1119.html', 'artcheck_1124.html')
assert 'artcheck_1124.html' in s and 'amamitomochika' in s and '11/24 の記事3本' in s
exec(compile(s, 'mk', 'exec'))
