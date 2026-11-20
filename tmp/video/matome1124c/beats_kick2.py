# -*- coding: utf-8 -*-
# 11/10 第4版の拍：133.18BPM・キックの位相を 4 秒窓（3 秒おき）で追う（beats_late.txt）
#   キックは 0〜45 秒で 0.22〜0.30 にそろい、45 秒から 0.30→0.44 へゆっくり遅れる（終わりへ向けて少しゆるむ）＝窓の中央値（3窓）でならして追う
#   スネアはスウィングで裏と表を行き来する（0.00／0.22／0.45）＝合わせる相手にしない → beats.json・beats_kick2.txt
import io, json
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = io.open(D + 'tempo_fine.py', encoding='utf-8').read()
src = src[:src.index("print('① 134.0BPM")]
G = {}
exec(compile(src, 'tf', 'exec'), G)
SN, K, T, fit = G['SN'], G['K'], G['T'], G['fit']
BPM, END = 133.18, 58.3
P = 60 / BPM
cs, phs = [], []
for a in np.arange(0, 58, 3.0):
    s, ph = fit(K, BPM, a, a + 4, 0.002)
    cs.append(a + 2); phs.append(ph)
un = [phs[0]]
for p in phs[1:]:
    q = p
    while q - un[-1] > P / 2: q -= P
    while q - un[-1] < -P / 2: q += P
    un.append(q)
sm = [float(np.median(un[max(0, i - 1):i + 2])) for i in range(len(un))]
beats, n = [], 0
while True:
    t = n * P + float(np.interp(n * P, cs, sm))
    if t > END: break
    if t >= 0: beats.append(round(t, 3))
    n += 1


def strength(env, bs):
    bs = np.asarray(bs)
    if not len(bs):
        return float('nan')
    idx = np.clip(np.searchsorted(T, bs), 0, len(env) - 1)
    return float(env[idx].mean() / env.mean())


iv = np.diff(beats)
out = ['窓の位相 ' + ' '.join('%.0f:%.3f' % (c, p) for c, p in zip(cs, sm)), '拍 %d 間隔 %.3f〜%.3f' % (len(beats), iv.min(), iv.max()),
       '全体 スネア %.2f キック %.2f' % (strength(SN, beats), strength(K, beats))]
for a in range(0, 60, 10):
    nn = [b for b in beats if a <= b < a + 10]
    out.append('  %2d〜%2d秒 スネア %.2f キック %.2f' % (a, a + 10, strength(SN, nn), strength(K, nn)))
json.dump({'bpm': BPM, 'beats': beats}, io.open(D + 'beats.json', 'w'))
io.open(D + 'beats_kick2.txt', 'w', encoding='utf-8').write('\n'.join(out))
