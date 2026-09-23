# -*- coding: utf-8 -*-
"""id13820 の下書きジャンル `_genre` を、楽天のカテゴリ（/event/）どおり event にする。

🚨ここは「人が決める」枠ではない＝売り場の言うとおりに写すのが決まり
   （[[feedback_genre_pia_asis_and_other]]）。道具側（tools/rakuten_harvest.py の PATH_GENRE）
   にも最後の砦 ('/event/', 'event') を足したので、次からは空にならない。
🚨index.html は CRLF のまま書き戻す（[[feedback_index_html_crlf_preserve]]）。
"""
import io, sys
sys.stdout.reconfigure(encoding='utf-8')

P = 'index.html'
b = io.open(P, 'rb').read()
crlf0, lf0 = b.count(b'\r\n'), b.count(b'\n')
h = b.decode('utf-8')

OLD = '"id": 13820,'
i = h.find(OLD)
assert i > 0, 'id13820 が見つからない'
j = h.find('"_genre": ""', i)
assert 0 < j < i + 2000, '_genre が近くに無い（%d）' % j
h2 = h[:j] + '"_genre": "event"' + h[j + len('"_genre": ""'):]

out = h2.encode('utf-8')
assert out.count(b'\n') == lf0 and out.count(b'\r\n') == crlf0, '改行が変わった'
io.open(P, 'wb').write(out)
print('id13820 の _genre を event にした（CRLF %d 本そのまま）' % crlf0)
