# -*- coding: utf-8 -*-
# きゅ〜くるの行をアイドル劇場の行にまとめて区切りが 12 個になった＝売り場 9・公演 10・締め 11 に番号を直す
import io
D = 'C:/Users/user/oshinavi/tmp/video/matome1124l/'
s = io.open(D + 'make_spec.py', encoding='utf-8').read()
for a, b in (('LOW = {10, 11}', 'LOW = {9, 10}'),
             ("CHORUS_AT, URL_AT = chunks[10]['show'], chunks[12]['show']", "CHORUS_AT, URL_AT = chunks[9]['show'], chunks[11]['show']"),
             ("chunks[12]['cy'] = 1080", "chunks[11]['cy'] = 1080")):
    assert s.count(a) == 1, a
    s = s.replace(a, b)
io.open(D + 'make_spec.py', 'w', encoding='utf-8').write(s)
print('ok')
