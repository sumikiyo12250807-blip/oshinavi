# -*- coding: utf-8 -*-
# 10秒窓ごとにキックとスネアの位相（129.2BPM）と当たりを並べる → phase_1113.txt
import io
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = io.open(D + 'tempo_fine.py', encoding='utf-8').read()
src = src[:src.index("print('① 134.0BPM")]
G = {}
exec(compile(src, 'tf', 'exec'), G)
SN, K, fit = G['SN'], G['K'], G['fit']
out = []
for bpm in (128.9, 129.0, 129.1, 129.2):
    out.append('== %.1f BPM（1拍 %.3f 秒）' % (bpm, 60 / bpm))
    for a in range(0, 106, 8):
        sk, pk = fit(K, bpm, a, a + 8, 0.002)
        ss, ps = fit(SN, bpm, a, a + 8, 0.002)
        out.append('  %3d秒 キック 位相 %.3f 当たり %.2f ｜ スネア 位相 %.3f 当たり %.2f' % (a, pk, sk, ps, ss))
io.open(D + 'phase_1113.txt', 'w', encoding='utf-8').write('\n'.join(out))
