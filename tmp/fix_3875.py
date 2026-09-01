# -*- coding: utf-8 -*-
"""id3875 ミュージカル「タイムトラベラーズ・ワイフ」に、ヒールが消した
「予定枚数終了」の枠2つ（東京・大阪）を戻す。

売り切れた枠は消さずに「予定枚数終了」で表示し続ける決まり
（memory: feedback_soldout_keep_visible）。昼のヒールが再パース結果で
tickets を丸ごと置き換えたため、soldout 枠が落ちていた。
🚨index.html は newline='' で読み書きして改行を壊さない。
"""
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'

OLD = (
    '    "tickets": [\r\n'
    '      {\r\n'
    '        "type": "追加席発売（東京 9/5〜9/24公演）9/2 20:00発売",\r\n'
    '        "date": "2026-09-02",\r\n'
    '        "startDate": "2026-09-02"\r\n'
    '      }\r\n'
    '    ],\r\n'
    '    "verified": true,\r\n'
    '    "verifiedAt": "2026-08-06"\r\n'
)
NEW = (
    '    "tickets": [\r\n'
    '      {\r\n'
    '        "type": "追加席発売（東京 9/5〜9/24公演）9/2 20:00発売",\r\n'
    '        "date": "2026-09-02",\r\n'
    '        "startDate": "2026-09-02"\r\n'
    '      },\r\n'
    '      {\r\n'
    '        "type": "一般発売（東京 9/5〜9/24公演）8/8 10:00発売",\r\n'
    '        "date": "2026-08-08",\r\n'
    '        "startDate": "2026-08-08",\r\n'
    '        "soldout": true,\r\n'
    '        "soldoutSince": "2026-08-09"\r\n'
    '      },\r\n'
    '      {\r\n'
    '        "type": "一般発売（大阪 10/2〜10/8公演）8/8 10:00発売",\r\n'
    '        "date": "2026-08-08",\r\n'
    '        "startDate": "2026-08-08",\r\n'
    '        "soldout": true,\r\n'
    '        "soldoutSince": "2026-08-09"\r\n'
    '      }\r\n'
    '    ],\r\n'
    '    "verified": true,\r\n'
    '    "verifiedAt": "2026-08-06"\r\n'
)

s = io.open(P, encoding='utf-8', newline='').read()
n = s.count(OLD)
print('match =', n)
if n != 1:
    print('!! 一意に決まらないので中止')
    sys.exit(1)
io.open('index.html.bak_0901_fix3875', 'w', encoding='utf-8', newline='').write(s)
io.open(P, 'w', encoding='utf-8', newline='').write(s.replace(OLD, NEW))
b = open(P, 'rb').read()
print('CRLF=%d bare_LF=%d CRCRLF=%d' % (b.count(b'\r\n'), b.count(b'\n') - b.count(b'\r\n'), b.count(b'\r\r\n')))
print('DONE')
