# -*- coding: utf-8 -*-
# 11/25 記事3本の確認ページ（本文＋出典URL）→ artcheck_1125.html（x1119/art19/mk_page.py の形）
import io
A = 'C:/Users/user/oshinavi/tmp/x1125/art25/'
s = io.open('C:/Users/user/oshinavi/tmp/x1119/art19/mk_page.py', encoding='utf-8').read()
s = s.replace("A = 'C:/Users/user/oshinavi/tmp/x1119/art19/'", "A = '%s'" % A)
s = s.replace("ARTS = [('daibakushow', 'DAIBAKUSHOW 2026'), ('asagaya', '阿佐ヶ谷姉妹 ミーツ オーケストラ'), ('plastictree', 'Plastic Tree 年末公演')]",
              "ARTS = [('harunoutaikai', '春の謡会2027（大槻能楽堂）'), ('mayj_kidsjazz', 'Kids meet Jazz! with May J.'), ('tokiasako', '土岐麻子 Yokosuka Bayside Breeze vol.8')]")
a = s.index('NOTES = ['); b = s.index(']\n', a) + 2
s = s[:a] + '''NOTES = [
    '独立の確かめ（別の係が公式と売り場のページを自分で開き直した・日付・曜日・時刻・料金・受付期間は3本とも一致）＝🔴0🟠1🟡6 → 直したわ',
    '土岐麻子：「11月29日（日）10:00〜」の引用は劇場サイトの文字と違った（時刻はチラシだけ）ので、その1行を外した／学生券と会員の金額は計算した値だったので「一般の半額」「10%OFF」に／中国ツアーは「発表されていた」に／俱→倶／これまでの顔ぶれは「Vol.1〜Vol.6」と書いた',
    'May J.：今年2月の前回公演の7行は、出どころが非公式の一覧だけだったので外した（1,174字になった）／子ども料金の年齢は書かない決まりどおり「中学生以下」だけ',
    '春の謡会：主催は大阪府・大阪市・大阪文化芸術事業実行委員会／1/30 の出演者は FANY と特設サイトどおり3人（かやゆー・さとう。・山田将司）＝OSHINAVI のカードも直したわ',
    '11/21・11/23 の記事6本もまだ OK 待ちよ',
]
''' + s[b:]
s = s.replace('<h1>11/19 の記事3本（11/21・11/22 発売の組）</h1>', '<h1>11/25 の記事3本（11/26・11/28・11/29 発売の組）</h1>').replace('artcheck_1119.html', 'artcheck_1125.html')
assert 'artcheck_1125.html' in s and 'harunoutaikai' in s and '11/25 の記事3本' in s
exec(compile(s, 'mk', 'exec'))
