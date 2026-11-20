# -*- coding: utf-8 -*-
# 11/14 お笑い（67.6秒）：tempo_check 1位＝101.0BPM（スネア 7.05）→ 100.5〜101.5 を 0.05 刻みでスネアに当て直し、
#   10秒ごとの位相が揃うかを見る → beats.json（等間隔の格子・寄せない）
import io, json
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = io.open(D + 'tempo_fine.py', encoding='utf-8').read()
src = src[:src.index("print('① 134.0BPM")]
G = {}
exec(compile(src, 'tf', 'exec'), G)
SN, K, T, fit = G['SN'], G['K'], G['T'], G['fit']
END = 97.0
sc = sorted(((fit(SN, b, 1, 95.8, 0.002) + (b,)) for b in np.arange(72.3, 73.31, 0.02)), reverse=True)[:5]
out = ['候補 ' + str([(round(s, 2), round(b, 2), round(p, 3)) for s, p, b in sc])]
s, ph, B = sc[0]
P = 60 / B
out.append('採用 %.2fBPM 位相 %.3f 当たり %.2f' % (B, ph, s))
for a in range(0, 100, 10):
    s2, p2 = fit(SN, B, a, a + 10, 0.002)
    out.append('  %2d〜%2d秒 最良位相 %.3f（格子との差 %+.3f）点 %.2f' % (a, a + 10, p2, ((p2 - ph + P / 2) % P) - P / 2, s2))
beats = [round(ph + n * P, 3) for n in range(int((END - ph) / P) + 1)]


def strength(env, bs):
    bs = np.asarray(bs)
    idx = np.clip(np.searchsorted(T, bs), 0, len(env) - 1)
    return float(env[idx].mean() / env.mean())


for a in range(0, 100, 10):
    nn = [b for b in beats if a <= b < a + 10]
    out.append('  %2d〜%2d秒 スネア %.2f キック %.2f' % (a, a + 10, strength(SN, nn), strength(K, nn)))
out.append('拍 %d 本・間隔 %.3f' % (len(beats), P))
json.dump({'bpm': round(B, 2), 'beats': beats}, io.open(D + 'beats.json', 'w'))
io.open(D + 'beats_1124c.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
