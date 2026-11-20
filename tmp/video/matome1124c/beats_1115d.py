# -*- coding: utf-8 -*-
# 11/15 お笑い：101.9BPM の格子は 90 秒からずれる（スネア 0.59→0.02）＝終わり（86 秒〜）だけ位相を当て直して継ぐ
import io, json
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = io.open(D + 'tempo_fine.py', encoding='utf-8').read()
src = src[:src.index("print('① 134.0BPM")]
G = {}
exec(compile(src, 'tf', 'exec'), G)
SN, K, T, fit = G['SN'], G['K'], G['T'], G['fit']
ENV = K / K.mean() + SN / SN.mean()
END, CUT = 108.6, 86.0
P = 60 / 101.9
s1, ph1 = fit(SN, 101.9, 8, 86, 0.001)
out = ['前半 位相 %.3f 当たり %.2f' % (ph1, s1)]
best = None
for bpm in np.arange(100.5, 103.01, 0.1):
    for env_name, env in (('snare', SN), ('both', ENV)):
        s2, ph2 = fit(env, bpm, CUT, END, 0.002)
        if best is None or s2 > best[0]:
            best = (s2, bpm, ph2, env_name)
out.append('後半 いちばん当たる %.1fBPM 位相 %.3f 当たり %.2f（%s）' % (best[1], best[2], best[0], best[3]))
s2, B2, ph2, _ = best
P2 = 60 / B2
A = [round(ph1 + n * P, 3) for n in range(int((CUT - ph1) / P) + 1)]
Bb = [round(ph2 + n * P2, 3) for n in range(int((END - ph2) / P2) + 1)]
Bb = [b for b in Bb if b > A[-1] + 0.6 * P]
beats = A + Bb


def strength(env, bs):
    bs = np.asarray(bs)
    idx = np.clip(np.searchsorted(T, bs), 0, len(env) - 1)
    return float(env[idx].mean() / env.mean())


iv = np.diff(beats)
out.append('拍 %d 間隔 %.3f〜%.3f（継ぎ目 %.3f→%.3f）' % (len(beats), iv.min(), iv.max(), A[-1], Bb[0] if Bb else -1))
for a in range(0, 110, 10):
    nn = [b for b in beats if a <= b < a + 10]
    out.append('  %3d〜%3d秒 スネア %.2f キック %.2f' % (a, a + 10, strength(SN, nn), strength(K, nn)))
json.dump({'bpm': 101.9, 'beats': beats}, io.open(D + 'beats.json', 'w'))
io.open(D + 'beats_1115d.txt', 'w', encoding='utf-8').write('\n'.join(out))
