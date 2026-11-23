# -*- coding: utf-8 -*-
# 11/23 記事3本の確認ページ（本文＋出典URL）→ artcheck_1123.html（x1119/art19/mk_page.py の形）
import io
A = 'C:/Users/user/oshinavi/tmp/x1123/art23/'
s = io.open('C:/Users/user/oshinavi/tmp/x1119/art19/mk_page.py', encoding='utf-8').read()
s = s.replace("A = 'C:/Users/user/oshinavi/tmp/x1119/art19/'", "A = '%s'" % A)
s = s.replace("ARTS = [('daibakushow', 'DAIBAKUSHOW 2026'), ('asagaya', '阿佐ヶ谷姉妹 ミーツ オーケストラ'), ('plastictree', 'Plastic Tree 年末公演')]",
              "ARTS = [('kaihonaoto', '海宝直人『ever after』'), ('ozonemakoto', '小曽根真『Now and Beyond! Vol.1』'), ('omiyayoshimoto', '大宮よしもと 年末寄席')]")
a = s.index('NOTES = ['); b = s.index(']\n', a) + 2
s = s[:a] + '''NOTES = [
    '独立の確かめ（別の係が出典のページを自分で開き直した・「」の引用は元の文字と一致・曜日は暦で計算）＝🔴3🟠3🟡6 → 直したわ',
    '海宝直人：e+ は12月だけでなく 1/3〜1/5 の回も 11/25 11:00 から受け付ける＝「12月の回」を「東京の回」に直した／OSHINAVI のカードにも e+ の1月の4回を足した（売り場と21枠とも一致）',
    '海宝直人：ローソンチケットの名前は外した（OSHINAVI はローチケを載せていないので）',
    '🆕 海宝直人：すちこ「ドリンク付きは書いて」で、愛知の料金を公式どおり「1ドリンク付きの13,600円」に直したわ（「ドリンクは書かない」はあたしが勝手に作った決まりだった＝外した）',
    '小曽根真：ぴあの先行は売り場の名前どおり「poco会員限定先行」に',
    '大宮よしもと：「1回の申し込みで1公演・10枚まで」「席を選んで買える」は買い方の条件なので外した／12/27 の2回のカードに 男性ブランコ・コットン を足した（FANY どおり）',
    '大宮よしもと：1行目の名前は日替わりの出演なので劇場名にしたわ',
    '11/21 の3本（Monte-Cristo・渡辺美里と京フィル・一富士茄子牛焦げルギー）もまだ OK 待ちよ＝ https://claude.ai/artifact/Ud4539xduoPp88v14bEEAv',
]
''' + s[b:]
s = s.replace('<h1>11/19 の記事3本（11/21・11/22 発売の組）</h1>', '<h1>11/23 の記事3本（11/25・11/27 発売の組）</h1>').replace('artcheck_1119.html', 'artcheck_1123.html')
assert 'artcheck_1123.html' in s and 'kaihonaoto' in s and '11/23 の記事3本' in s
exec(compile(s, 'mk', 'exec'))
