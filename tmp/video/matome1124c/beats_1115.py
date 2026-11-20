# -*- coding: utf-8 -*-
# 11/15 お笑い：拍＝スネアに当てた等間隔の格子
#   tempo_check：スネア 1位 101.8・2位 68.2（＝135.8 の2拍目4拍目）・全帯域 135.8 ＝ 135.8 前後で、10秒ごとのスネアの位相がいちばん揃う BPM を選ぶ
import io, json
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = io.open(D + 'tempo_fine.py', encoding='utf-8').read()
src = src[:src.index("print('① 134.0BPM")]
G = {}
exec(compile(src, 'tf', 'exec'), G)
SN, K, T, fit = G['SN'], G['K'], G['T'], G['fit']
END = 108.5
out = []


def unwrap(phs, P):
    un = [phs[0]]
    for p in phs[1:]:
        q = p
        while q - un[-1] > P / 2: q -= P
        while q - un[-1] < -P / 2: q += P
        un.append(q)
    return un


rows = []
for bpm in np.arange(135.2, 136.41, 0.05):
    P = 60 / bpm
    phs, sc = [], []
    for a in np.arange(4, 100, 12.0):
        s, ph = fit(SN, bpm, a, a + 12, 0.002)
        phs.append(ph); sc.append(s)
    un = unwrap(phs, P)
    rows.append((max(un) - min(un), round(float(bpm), 2), float(np.mean(sc)), float(np.median(un)) % P))
rows.sort()
out.append('流れ幅の小さい順 ' + ' '.join('%.2f:幅%.3f/当たり%.2f' % (b, w, s) for w, b, s, _ in rows[:6]))
BPM = rows[0][1]
s, ph = fit(SN, BPM, 4, 104, 0.001)
P = 60 / BPM
beats = [round(ph + n * P, 3) for n in range(int((END - ph) / P) + 1)]


def strength(env, bs):
    bs = np.asarray(bs)
    idx = np.clip(np.searchsorted(T, bs), 0, len(env) - 1)
    return float(env[idx].mean() / env.mean())


out.append('%.2fBPM 位相 %.3f（スネアの当たり %.2f）拍 %d' % (BPM, ph, s, len(beats)))
out.append('全体 スネア %.2f キック %.2f ／ 半拍ずらすと スネア %.2f' % (strength(SN, beats), strength(K, beats), strength(SN, [b + P / 2 for b in beats])))
for a in range(0, 110, 10):
    nn = [b for b in beats if a <= b < a + 10]
    out.append('  %3d〜%3d秒 スネア %.2f キック %.2f' % (a, a + 10, strength(SN, nn), strength(K, nn)))
json.dump({'bpm': BPM, 'beats': beats}, io.open(D + 'beats.json', 'w'))
io.open(D + 'beats_1115.txt', 'w', encoding='utf-8').write('\n'.join(out))
