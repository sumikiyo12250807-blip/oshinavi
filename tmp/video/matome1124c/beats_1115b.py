# -*- coding: utf-8 -*-
# 11/15 お笑い：等間隔の 1 本の格子だと位相が流れる（幅 0.18〜0.35 秒）＝beats_1112b の形で、窓ごとに位相を追ってならす
#   135.6〜136.2 を 0.05 刻み・キック＋スネアの合計に 4 秒窓（2 秒ずらし）で当て、位相の流れがいちばん小さい BPM → 窓の位相を3つの中央値でならして拍を作る
import io, json
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = io.open(D + 'tempo_fine.py', encoding='utf-8').read()
src = src[:src.index("print('① 134.0BPM")]
G = {}
exec(compile(src, 'tf', 'exec'), G)
SN, K, T, fit = G['SN'], G['K'], G['T'], G['fit']
ENV = K / K.mean() + SN / SN.mean()
END = 108.6
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
for bpm in np.arange(135.6, 136.21, 0.05):
    P = 60 / bpm
    phs = []
    for a in np.arange(2, 104, 8.0):
        s, ph = fit(ENV, bpm, a, a + 8, 0.002)
        phs.append(ph)
    un = unwrap(phs, P)
    rows.append((max(un) - min(un), round(float(bpm), 2)))
rows.sort()
out.append('流れ幅の小さい順 ' + ' '.join('%.2f:%.3f' % (b, w) for w, b in rows[:6]))
BPM = rows[0][1]
P = 60 / BPM
cs, phs = [], []
for a in np.arange(0, END - 3, 2.0):
    s, ph = fit(ENV, BPM, a, a + 4, 0.002)
    cs.append(a + 2); phs.append(ph)
un = unwrap(phs, P)
sm = [float(np.median(un[max(0, i - 1):i + 2])) for i in range(len(un))]
beats, n = [], -4
while True:
    t = n * P + float(np.interp(n * P, cs, sm))
    if t > END: break
    if t >= 0: beats.append(round(t, 3))
    n += 1
iv = np.diff(beats)
out.append('%.2fBPM 拍 %d 間隔 %.3f〜%.3f' % (BPM, len(beats), iv.min(), iv.max()))
out.append('全体 キック %.2f スネア %.2f ／ 半拍ずらし キック %.2f スネア %.2f' % (strength(K, beats), strength(SN, beats), strength(K, [b + P / 2 for b in beats]), strength(SN, [b + P / 2 for b in beats])))
for a in range(0, 110, 10):
    nn = [b for b in beats if a <= b < a + 10]
    out.append('  %3d〜%3d秒 キック %.2f スネア %.2f' % (a, a + 10, strength(K, nn), strength(SN, nn)))
out.append('窓の位相 ' + ' '.join('%.0f:%.3f' % (c, p) for c, p in zip(cs, sm)))
json.dump({'bpm': BPM, 'beats': beats}, io.open(D + 'beats.json', 'w'))
io.open(D + 'beats_1115b.txt', 'w', encoding='utf-8').write('\n'.join(out))
