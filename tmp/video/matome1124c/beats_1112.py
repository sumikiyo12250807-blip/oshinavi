# -*- coding: utf-8 -*-
# 11/12：tempo_check の1位＝131.4BPM（全帯域・キック2位・スネア3位／65.6 はその半分）。
#   4 秒の窓ごとに 131.4 の格子を「キック＋スネア」に当てて位相を取り、3 窓の中央値でならして拍を作る（grid_beats2 の形）→ beats.json・beats_1112.txt
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
rows = []
for bpm in np.arange(130.6, 132.21, 0.05):
    P = 60 / bpm
    phs, sc = [], []
    for a in np.arange(2, 70, 8.0):
        s, ph = fit(ENV, bpm, a, a + 8, 0.002)
        phs.append(ph); sc.append(s)
    un = [phs[0]]
    for p in phs[1:]:
        q = p
        while q - un[-1] > P / 2: q -= P
        while q - un[-1] < -P / 2: q += P
        un.append(q)
    rows.append((max(un) - min(un), round(float(bpm), 2), float(np.mean(sc))))
rows.sort()
out.append('流れ幅の小さい順 ' + ' '.join('%.2f:%.3f/%.2f' % (b, s, c) for s, b, c in rows[:6]))
BPM = rows[0][1]
P = 60 / BPM
cs, phs = [], []
for a in np.arange(0, END - 3, 4.0):
    s, ph = fit(ENV, BPM, a, a + 4, 0.002)
    cs.append(a + 2); phs.append(ph)
un = [phs[0]]
for p in phs[1:]:
    q = p
    while q - un[-1] > P / 2: q -= P
    while q - un[-1] < -P / 2: q += P
    un.append(q)
sm = [float(np.median(un[max(0, i - 1):i + 2])) for i in range(len(un))]
beats, n = [], -4
while True:
    t = n * P + float(np.interp(n * P, cs, sm))
    if t > END: break
    if t >= 0: beats.append(round(t, 3))
    n += 1


def strength(env, bs):
    idx = np.clip(np.searchsorted(T, np.asarray(bs)), 0, len(env) - 1)
    return float(env[idx].mean() / env.mean())


iv = np.diff(beats)
out += ['BPM %.2f 拍 %d 間隔 %.3f〜%.3f' % (BPM, len(beats), iv.min(), iv.max()),
        '窓の位相 ' + ' '.join('%.0f:%.3f' % (c, p) for c, p in zip(cs, sm))]
half = [b + P / 2 for b in beats]
out.append('当たり 拍 キック %.2f スネア %.2f ／ 裏 キック %.2f スネア %.2f' % (strength(K, beats), strength(SN, beats), strength(K, half), strength(SN, half)))
for a in range(0, 80, 10):
    nn = [b for b in beats if a <= b < a + 10]
    out.append('  %3d〜%3d秒 キック %.2f スネア %.2f' % (a, a + 10, strength(K, nn), strength(SN, nn)))
json.dump({'bpm': BPM, 'beats': beats}, io.open(D + 'beats.json', 'w'))
io.open(D + 'beats_1112.txt', 'w', encoding='utf-8').write('\n'.join(out))
