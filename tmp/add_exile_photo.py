# -*- coding: utf-8 -*-
"""EXILE の写真を記事に追加する（2枚目の探索で見つかった）。

1回目の探索では「EXILE Japanese group」で GENERATIONS / THE RAMPAGE しか出ず
「素材なし」と結論していたが、ユーザー「使っていい画像は使う形で」を受けて
検索語を4ルートに増やしたら **本体の写真が出た**（[[feedback_verify_before_saying_impossible]]）。

  File:MTV VMAJ 2014 Exile.jpg
    CC BY-SA 2.0 / Norio NAKAYAMA / Restrictions なし
    2014年 MTV Video Music Awards Japan のレッドカーペット。黒スーツで並んで歩く姿。
    記事本文の「MATSU、ÜSA、MAKIDAI まで揃う顔ぶれ」に合う絵。
  🚨2014年の写真なので**キャプションに年を明記**する（今のメンバー構成と違うため）。
"""
import io, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SRC = 'index.html'
raw = open(SRC, 'rb').read()
before = raw.count(b'\r\n')
assert raw.count(b'\n') - before == 0, 'LF-only がある'
h = raw.decode('utf-8')

NL = '\r\n'
PAGE = 'https://commons.wikimedia.org/wiki/File:MTV_VMAJ_2014_Exile.jpg'
LICURL = 'https://creativecommons.org/licenses/by-sa/2.0/deed.ja'

fig = (
    '        <figure class="pk-fig">' + NL +
    '          <img src="img/exile.jpg" alt="黒いスーツ姿でレッドカーペットを歩くEXILEのメンバー'
    '（2014年 MTV Video Music Awards Japan）" width="1000" height="667" loading="lazy" decoding="async">' + NL +
    '          <figcaption>2014年 MTV VMAJ／Photo: '
    '<a href="%s" target="_blank" rel="noopener">Norio NAKAYAMA</a> '
    '(<a href="%s" target="_blank" rel="noopener">CC BY-SA 2.0</a>)</figcaption>' % (PAGE, LICURL) + NL +
    '        </figure>' + NL
)

i = h.find('<span class="pk-name">EXILE</span>')
assert i > 0, 'EXILE の見出しが見つからない'
tag = '<div class="pk-detail" hidden>' + NL
j = h.find(tag, i)
assert j > i, 'EXILE の pk-detail が見つからない'
assert 'img/exile.jpg' not in h, 'すでに入っている'
ins = j + len(tag)
h = h[:ins] + fig + h[ins:]

out = h.encode('utf-8')
after = out.count(b'\r\n')
lf = out.count(b'\n') - after
assert lf == 0, 'LF が混ざった'
open(SRC, 'wb').write(out)
print('EXILE の写真を追加 / CRLF %d → %d（LF-only %d）/ 図の数 %d'
      % (before, after, lf, h.count('class="pk-fig')))
