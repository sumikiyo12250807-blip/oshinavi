# -*- coding: utf-8 -*-
# 11/10 お笑い 11/13（1:47・129BPM 前後）の拍：①128.6〜129.4 を 0.02 刻みで、10秒窓ごとのキックの位相の流れ幅が最小の BPM を選ぶ
#   ②そのBPMでキックの位相を4秒窓（3秒おき）で追い、3窓の中央値でならす（matome1110o の第4版 beats_kick2 と同じ形）→ beats.json・beats_1113.txt
import io, json
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = io.open(D + 'tempo_fine.py', encoding='utf-8').read()
src = src[:src.index("print('① 134.0BPM")]
G = {}
exec(compile(src, 'tf', 'exec'), G)
SN, K, T, fit = G['SN'], G['K'], G['T'], G['fit']
END = 106.0
out = []


def unwrap(phs, P):
    un = [phs[0]]
    for p in phs[1:]:
        q = p
        while q - un[-1] > P / 2: q -= P
        while q - un[-1] < -P / 2: q += P
        un.append(q)
    return un


best = None
for bpm in np.arange(128.6, 129.41, 0.02):
    P = 60 / bpm
    phs, sc = [], []
    for a in np.arange(0, 100, 10.0):
        s, ph = fit(K, bpm, a, a + 10, 0.002)
        phs.append(ph); sc.append(s)
    un = unwrap(phs, P)
    spread = max(un) - min(un)
    if best is None or spread < best[0]:
        best = (spread, round(float(bpm), 2), float(np.mean(sc)))
out.append('いちばん位相がそろう BPM %.2f（流れ幅 %.3f 秒・当たり %.2f）' % (best[1], best[0], best[2]))
BPM = best[1]
P = 60 / BPM
cs, phs = [], []
for a in np.arange(0, END, 3.0):
    s, ph = fit(K, BPM, a, a + 4, 0.002)
    cs.append(a + 2); phs.append(ph)
un = unwrap(phs, P)
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
out += ['窓の位相 ' + ' '.join('%.0f:%.3f' % (c, p) for c, p in zip(cs, sm)), '拍 %d 間隔 %.3f〜%.3f' % (len(beats), iv.min(), iv.max()),
        '全体 スネア %.2f キック %.2f' % (strength(SN, beats), strength(K, beats))]
for a in range(0, 110, 10):
    nn = [b for b in beats if a <= b < a + 10]
    out.append('  %3d〜%3d秒 スネア %.2f キック %.2f' % (a, a + 10, strength(SN, nn), strength(K, nn)))
json.dump({'bpm': BPM, 'beats': beats}, io.open(D + 'beats.json', 'w'))
io.open(D + 'beats_1113.txt', 'w', encoding='utf-8').write('\n'.join(out))
