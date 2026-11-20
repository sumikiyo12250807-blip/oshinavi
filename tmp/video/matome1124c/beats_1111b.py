# -*- coding: utf-8 -*-
# 11/11：96BPM で追うと 28 秒・36 秒で位相が半拍ずつ跳ぶ（強い音が表と裏で入れ替わる）＝倍の 192 前後の格子で位相を追い、
#   そのあと「1つおき」の組をキックの強い方で選ぶ（kooza1110 の 158/79 と同じ形）→ beats.json・beats_1111b.txt
import io, json
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = io.open(D + 'tempo_fine.py', encoding='utf-8').read()
src = src[:src.index("print('① 134.0BPM")]
G = {}
exec(compile(src, 'tf', 'exec'), G)
SN, K, T, fit = G['SN'], G['K'], G['T'], G['fit']
ENV = K / K.mean() + SN / SN.mean()
END = 75.6
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
for bpm in np.arange(190.8, 193.21, 0.04):
    P = 60 / bpm
    phs, sc = [], []
    for a in np.arange(2, 70, 8.0):
        s, ph = fit(ENV, bpm, a, a + 8, 0.002)
        phs.append(ph); sc.append(s)
    un = unwrap(phs, P)
    rows.append((max(un) - min(un), round(float(bpm), 2), float(np.mean(sc))))
rows.sort()
out.append('192 前後 流れ幅の小さい順 ' + ' '.join('%.2f:%.3f/%.2f' % (b, s, c) for s, b, c in rows[:6]))
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
ka, kb = strength(K, A), strength(K, B)
beats = A if ka >= kb else B
out.append('192 の格子 %d 本 → 1つおき：組A キック %.2f スネア %.2f ／ 組B キック %.2f スネア %.2f → %s' % (
    len(fine), ka, strength(SN, A), kb, strength(SN, B), 'A' if ka >= kb else 'B'))
iv = np.diff(beats)
out += ['拍 %d 間隔 %.3f〜%.3f BPM %.2f' % (len(beats), iv.min(), iv.max(), BPM2 / 2),
        '窓の位相 ' + ' '.join('%.0f:%.3f' % (c, p) for c, p in zip(cs, sm))]
for a in range(0, 80, 10):
    nn = [b for b in beats if a <= b < a + 10]
    out.append('  %3d〜%3d秒 キック %.2f スネア %.2f' % (a, a + 10, strength(K, nn), strength(SN, nn)))
json.dump({'bpm': BPM2 / 2, 'beats': beats}, io.open(D + 'beats.json', 'w'))
io.open(D + 'beats_1111b.txt', 'w', encoding='utf-8').write('\n'.join(out))
