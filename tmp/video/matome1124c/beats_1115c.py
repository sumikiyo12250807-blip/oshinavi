# -*- coding: utf-8 -*-
# 11/15 お笑い：拍＝スネアに当てた等間隔（101.9BPM）
#   phase_1115：101.9 はスネアの位相が 14〜86 秒で 0.420〜0.448（流れ幅 0.028）・当たり 6.8〜8.7 ＝いちばん揃う（135.8 は窓ごとに位相がばらばら）
import io, json
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = io.open(D + 'tempo_fine.py', encoding='utf-8').read()
src = src[:src.index("print('① 134.0BPM")]
G = {}
exec(compile(src, 'tf', 'exec'), G)
SN, K, T, fit = G['SN'], G['K'], G['T'], G['fit']
BPM, END = 101.9, 108.6
s, ph = fit(SN, BPM, 8, 96, 0.001)
P = 60 / BPM
beats = [round(ph + n * P, 3) for n in range(int((END - ph) / P) + 1)]


def strength(env, bs):
    bs = np.asarray(bs)
    idx = np.clip(np.searchsorted(T, bs), 0, len(env) - 1)
    return float(env[idx].mean() / env.mean())


out = ['%.1fBPM 位相 %.3f（スネアの当たり %.2f）拍 %d' % (BPM, ph, s, len(beats)),
       '全体 スネア %.2f キック %.2f ／ 半拍ずらし スネア %.2f' % (strength(SN, beats), strength(K, beats), strength(SN, [b + P / 2 for b in beats]))]
for a in range(0, 110, 10):
    nn = [b for b in beats if a <= b < a + 10]
    out.append('  %3d〜%3d秒 スネア %.2f キック %.2f' % (a, a + 10, strength(SN, nn), strength(K, nn)))
json.dump({'bpm': BPM, 'beats': beats}, io.open(D + 'beats.json', 'w'))
io.open(D + 'beats_1115c.txt', 'w', encoding='utf-8').write('\n'.join(out))
