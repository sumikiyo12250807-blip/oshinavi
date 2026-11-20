# -*- coding: utf-8 -*-
# 11/10：拍の位相が 131.6BPM で 0.21→0.88 秒まで流れた＝本当の BPM を 128〜135 で測り直す（スネア＋キック）
#   各 BPM で 10 秒窓ごとの位相がそろうか（流れ幅）と、全体の当たりを出す → tempo1110.txt（beats.json は書かない）
import io, sys
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = io.open(D + 'tempo_fine.py', encoding='utf-8').read()
src = src[:src.index("print('① 134.0BPM")]
G = {}
exec(compile(src, 'tf', 'exec'), G)
SN, K, fit = G['SN'], G['K'], G['fit']
out = []
for bpm in np.arange(128.0, 135.01, 0.25):
    P = 60 / bpm
    s_all, _ = fit(SN, bpm, 1, 57, 0.004)
    k_all, _ = fit(K, bpm, 1, 57, 0.004)
    phs = []
    for a in range(0, 56, 8):
        phs.append(fit(SN + K, bpm, a, a + 8, 0.004)[1])
    un = [phs[0]]
    for p in phs[1:]:
        q = p
        while q - un[-1] > P / 2: q -= P
        while q - un[-1] < -P / 2: q += P
        un.append(q)
    out.append('%.2f スネア %.2f キック %.2f 位相 %s 流れ幅 %.3f' % (bpm, s_all, k_all, ' '.join('%.2f' % p for p in un), max(un) - min(un)))
io.open(D + 'tempo1110.txt', 'w', encoding='utf-8').write('\n'.join(out))
