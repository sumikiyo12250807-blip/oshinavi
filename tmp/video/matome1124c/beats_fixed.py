# -*- coding: utf-8 -*-
# 11/10 第3版の拍：窓ごとに位相を追うと半拍とびが混じった（当たり スネア 1.84）
#   tempo_check の1位＝キック 133.2BPM@0.188・全帯域 133.2@0.169 ＝1本の等間隔の格子にする（10/31 と同じ・寄せない）
#   133.0〜133.3 × 位相を 0.002 刻みでスネア＋キックに当て、裏（＋半拍）とも並べて 10 秒ごとの当たりを出す → beats.json・beats_fixed.txt
import io, json, sys
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = io.open(D + 'tempo_fine.py', encoding='utf-8').read()
src = src[:src.index("print('① 134.0BPM")]
G = {}
exec(compile(src, 'tf', 'exec'), G)
SN, K, T, fit = G['SN'], G['K'], G['T'], G['fit']
END = 58.0
ALL = SN / SN.mean() + K / K.mean()
best = max((fit(ALL, b, 0.5, END, 0.002) + (b,)) for b in np.arange(133.0, 133.31, 0.02))
s, ph, bpm = best
P = 60 / bpm


def strength(env, bs):
    idx = np.clip(np.searchsorted(T, bs), 0, len(env) - 1)
    return float(env[idx].mean() / env.mean())


out = ['最良 %.2fBPM 位相 %.3f 当たり %.2f' % (bpm, ph, s)]
for name, p0 in (('表', ph), ('裏', ph + P / 2)):
    bs = np.arange(p0, END, P)
    out.append('%s 全体 スネア %.2f キック %.2f' % (name, strength(SN, bs), strength(K, bs)))
    for a in range(0, 60, 10):
        nn = bs[(bs >= a) & (bs < a + 10)]
        out.append('   %2d〜%2d秒 スネア %.2f キック %.2f' % (a, a + 10, strength(SN, nn), strength(K, nn)))
beats = [round(float(t), 3) for t in np.arange(ph, END, P)]
json.dump({'bpm': float(bpm), 'beats': beats}, io.open(D + 'beats.json', 'w'))
out.append('拍 %d 間隔 %.3f' % (len(beats), P))
io.open(D + 'beats_fixed.txt', 'w', encoding='utf-8').write('\n'.join(out))
