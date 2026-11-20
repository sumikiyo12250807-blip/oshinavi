# -*- coding: utf-8 -*-
# 11/16：96.7BPM の1本の格子は 40 秒すぎから後ろへ流れる（50〜60 で +0.12・70〜 で +0.22）＝後半だけテンポを当て直して2本の格子をつなぐ → beats.json
import io, json
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = io.open(D + 'tempo_fine.py', encoding='utf-8').read()
src = src[:src.index("print('① 134.0BPM")]
G = {}
exec(compile(src, 'tf', 'exec'), G)
SN, K, T, fit = G['SN'], G['K'], G['T'], G['fit']
out = []
s1, p1 = fit(SN, 96.7, 1, 40, 0.002)
B1, P1 = 96.7, 60 / 96.7
out.append('前半 96.70 位相 %.3f 点 %.2f' % (p1, s1))
# 後半：38〜75 秒で 95.5〜97.0 を当て直す（位相は 38 秒より前の格子からの続き具合も見る）
best = None
for b in np.arange(95.5, 97.01, 0.02):
    s, p = fit(SN, b, 38, 75, 0.002)
    s2, _ = fit(K, b, 38, 75, 0.002)
    if best is None or s + s2 > best[0]:
        best = (s + s2, b, p, s, s2)
_, B2, p2, s2a, s2b = best
P2 = 60 / B2
out.append('後半 %.2fBPM 位相 %.3f スネア %.2f キック %.2f' % (B2, p2, s2a, s2b))
beats = [p1 + n * P1 for n in range(int((40 - p1) / P1) + 1)]
# 40 秒より後は後半の格子で、前半の最後の拍からの間が 0.5〜1.5 拍になる所から始める
b2 = [p2 + n * P2 for n in range(int((75.5 - p2) / P2) + 1)]
b2 = [b for b in b2 if b > beats[-1] + 0.5 * P1]
beats += b2
beats = [round(b, 3) for b in beats]
for a in range(0, 80, 10):
    nn = np.asarray([b for b in beats if a <= b < a + 10])
    if len(nn):
        idx = np.clip(np.searchsorted(T, nn), 0, len(SN) - 1)
        out.append('  %2d〜%2d秒 スネア %.2f キック %.2f' % (a, a + 10, SN[idx].mean() / SN.mean(), K[idx].mean() / K.mean()))
d = np.diff(beats)
out.append('拍 %d 本・間隔 %.3f〜%.3f' % (len(beats), d.min(), d.max()))
json.dump({'bpm': round((B1 + B2) / 2, 2), 'beats': beats}, io.open(D + 'beats.json', 'w'))
io.open(D + 'beats_1116b.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
