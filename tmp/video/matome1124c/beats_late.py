# -*- coding: utf-8 -*-
# 11/10：40〜58 秒で格子が当たらない＝4 秒窓ごとに 133.18BPM の最良位相（スネア・キック別）と当たりを見る → beats_late.txt
import io
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = io.open(D + 'tempo_fine.py', encoding='utf-8').read()
src = src[:src.index("print('① 134.0BPM")]
G = {}
exec(compile(src, 'tf', 'exec'), G)
SN, K, fit = G['SN'], G['K'], G['fit']
P = 60 / 133.18
out = []
for a in np.arange(0, 58, 3.0):
    s1, p1 = fit(SN, 133.18, a, a + 4, 0.002)
    s2, p2 = fit(K, 133.18, a, a + 4, 0.002)
    out.append('%4.0f〜%4.0f スネア 位相 %.3f 当たり %.2f ｜ キック 位相 %.3f 当たり %.2f' % (a, a + 4, p1, s1, p2, s2))
out.append('（拍 %.3f 秒・格子の位相 0.226）' % P)
io.open(D + 'beats_late.txt', 'w', encoding='utf-8').write('\n'.join(out))
