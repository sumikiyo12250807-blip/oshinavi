# -*- coding: utf-8 -*-
# 11/12：131.5 で追うと 30・38・50 秒で位相が半拍ずつ跳ぶ（11/11 と同じ）＝倍の 263 前後の格子で位相を追い、
#   「1つおき」の組を キック＋スネア の強い方で選ぶ（beats_1111b の形）→ beats.json・beats_1112b.txt
import io, json
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = io.open(D + 'tempo_fine.py', encoding='utf-8').read()
src = src[:src.index("print('① 134.0BPM")]
G = {}
exec(compile(src, 'tf', 'exec'), G)
SN, K, T, fit = G['SN'], G['K'], G['T'], G['fit']
ENV = K / K.mean() + SN / SN.mean()
END = 76.3
out = []


def unwrap(phs, P):
    un = [phs[0]]
    for p in phs[1:]:
        q = p
        while q - un[-1] > P / 2: q -= P
        while q - un[-1] < -P / 2: q += P
        un.append(q)
    return un


def strength(env, bs):
    bs = np.asarray(bs)
    if not len(bs):
        return float('nan')
    idx = np.clip(np.searchsorted(T, bs), 0, len(env) - 1)
    return float(env[idx].mean() / env.mean())


rows = []
for bpm in np.arange(261.6, 264.41, 0.05):
    P = 60 / bpm
    phs, sc = [], []
    for a in np.arange(2, 70, 8.0):
        s, ph = fit(ENV, bpm, a, a + 8, 0.002)
        phs.append(ph); sc.append(s)
    un = unwrap(phs, P)
    rows.append((max(un) - min(un), round(float(bpm), 2), float(np.mean(sc))))
rows.sort()
out.append('263 前後 流れ幅の小さい順 ' + ' '.join('%.2f:%.3f/%.2f' % (b, s, c) for s, b, c in rows[:6]))
BPM2 = rows[0][1]
P2 = 60 / BPM2
cs, phs = [], []
for a in np.arange(0, END - 3, 2.0):
    s, ph = fit(ENV, BPM2, a, a + 4, 0.002)
    cs.append(a + 2); phs.append(ph)
un = unwrap(phs, P2)
sm = [float(np.median(un[max(0, i - 1):i + 2])) for i in range(len(un))]
fine, n = [], -4
while True:
    t = n * P2 + float(np.interp(n * P2, cs, sm))
    if t > END: break
    if t >= 0: fine.append(round(t, 3))
    n += 1
A, B = fine[0::2], fine[1::2]
ka, kb = strength(ENV, A), strength(ENV, B)
beats = A if ka >= kb else B
out.append('263 の格子 %d 本 → 1つおき：組A キック %.2f スネア %.2f ／ 組B キック %.2f スネア %.2f → %s' % (
    len(fine), strength(K, A), strength(SN, A), strength(K, B), strength(SN, B), 'A' if ka >= kb else 'B'))
iv = np.diff(beats)
out += ['拍 %d 間隔 %.3f〜%.3f BPM %.2f' % (len(beats), iv.min(), iv.max(), BPM2 / 2),
        '窓の位相 ' + ' '.join('%.0f:%.3f' % (c, p) for c, p in zip(cs, sm))]
other = B if beats is A else A
for a in range(0, 80, 10):
    nn = [b for b in beats if a <= b < a + 10]
    oo = [b for b in other if a <= b < a + 10]
    out.append('  %3d〜%3d秒 選んだ組 キック %.2f スネア %.2f ／ 裏 キック %.2f スネア %.2f' % (a, a + 10, strength(K, nn), strength(SN, nn), strength(K, oo), strength(SN, oo)))
json.dump({'bpm': BPM2 / 2, 'beats': beats}, io.open(D + 'beats.json', 'w'))
io.open(D + 'beats_1112b.txt', 'w', encoding='utf-8').write('\n'.join(out))
