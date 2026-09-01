# -*- coding: utf-8 -*-
"""id6101 角座でジョニーvol.8 に、ぴあの先行枠（〜9/6 23:59）を足す。

reconcile_pia --new の 🚨MISSING（ぴあ2枠 / 登録1枠）を潰す。
🚨index.html は改行を壊さないよう newline='' で読み書きし、置換は文字列そのままで行う
（memory: feedback_index_html_crlf_preserve / feedback_index_html_crcrlf_trap）。
"""
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'

OLD = (
    '    "tickets": [\r\n'
    '      {\r\n'
    '        "type": "一般発売（大阪 9/27公演）9/12 12:00発売",\r\n'
    '        "date": "2026-09-12",\r\n'
    '        "startDate": "2026-09-12"\r\n'
    '      }\r\n'
    '    ],\r\n'
    '    "verified": true,\r\n'
    '    "verifiedAt": "2026-09-01"\r\n'
    '  },\r\n'
    '  {\r\n'
    '    "id": 6102,\r\n'
)
NEW = (
    '    "tickets": [\r\n'
    '      {\r\n'
    '        "type": "先行（大阪 9/27公演）〜9/6 23:59",\r\n'
    '        "date": "2026-09-06"\r\n'
    '      },\r\n'
    '      {\r\n'
    '        "type": "一般発売（大阪 9/27公演）9/12 12:00発売",\r\n'
    '        "date": "2026-09-12",\r\n'
    '        "startDate": "2026-09-12"\r\n'
    '      }\r\n'
    '    ],\r\n'
    '    "verified": true,\r\n'
    '    "verifiedAt": "2026-09-01"\r\n'
    '  },\r\n'
    '  {\r\n'
    '    "id": 6102,\r\n'
)

s = io.open(P, encoding='utf-8', newline='').read()
n = s.count(OLD)
print('match =', n)
if n != 1:
    print('!! 一意に決まらないので中止')
    sys.exit(1)
io.open('index.html.bak_0901_fix6101', 'w', encoding='utf-8', newline='').write(s)
io.open(P, 'w', encoding='utf-8', newline='').write(s.replace(OLD, NEW))
b = open(P, 'rb').read()
print('CRLF=%d bare_LF=%d CRCRLF=%d' % (b.count(b'\r\n'), b.count(b'\n') - b.count(b'\r\n'), b.count(b'\r\r\n')))
print('DONE')
