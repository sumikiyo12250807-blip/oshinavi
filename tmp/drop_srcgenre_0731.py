# -*- coding: utf-8 -*-
"""振り分け後に残った下書きフィールド _srcgenre（楽天harvest由来）を削除する。
index.html はバイナリで読み書き（CRLF保護 [[feedback_index_html_crlf_preserve]]）。"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

p = 'index.html'
b = open(p, 'rb').read()
old = '    "_srcgenre": "rakuten",\r\n'.encode()
n = b.count(old)
print('該当行 =', n)
if n == 0:
    raise SystemExit('対象なし')
b2 = b.replace(old, b'')
print('bytes %d → %d（差 %d）' % (len(b), len(b2), len(b) - len(b2)))
print('残 _srcgenre =', b2.count('_srcgenre'.encode()))
assert b2.count(b'\n') - b2.count(b'\r\n') == 0, '単独LFが出た'
open(p, 'wb').write(b2)
print('書き戻し完了')
