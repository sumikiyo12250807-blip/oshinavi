# -*- coding: utf-8 -*-
# 11/13 お笑い：拍＝スネアに当てた等間隔（129.0BPM・位相は 8〜104 秒のスネアの当たりが最大の所）
#   phase_1113：129.0 はスネアの位相が 8〜104 秒で 0.360〜0.386（流れ幅 0.026）＝いちばん揃う。キックは 40 秒で裏へ移る＝相手にしない
import io, json
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = io.open(D + 'tempo_fine.py', encoding='utf-8').read()
src = src[:src.index("print('① 134.0BPM")]
G = {}
exec(compile(src, 'tf', 'exec'), G)
SN, K, T, fit = G['SN'], G['K'], G['T'], G['fit']
BPM, END = 129.0, 106.5
s, ph = fit(SN, BPM, 8, 104, 0.001)
P = 60 / BPM
beats = [round(ph + n * P, 3) for n in range(int((END - ph) / P) + 1)]


def strength(env, bs):
    bs = np.asarray(bs)
    idx = np.clip(np.searchsorted(T, bs), 0, len(env) - 1)
    return float(env[idx].mean() / env.mean())


out = ['129.0BPM 位相 %.3f（スネアの当たり %.2f）拍 %d' % (ph, s, len(beats)), '全体 スネア %.2f キック %.2f' % (strength(SN, beats), strength(K, beats))]
for a in range(0, 110, 10):
    nn = [b for b in beats if a <= b < a + 10]
    out.append('  %3d〜%3d秒 スネア %.2f キック %.2f' % (a, a + 10, strength(SN, nn), strength(K, nn)))
json.dump({'bpm': BPM, 'beats': beats}, io.open(D + 'beats.json', 'w'))
io.open(D + 'beats_grid_1113.txt', 'w', encoding='utf-8').write('\n'.join(out))
