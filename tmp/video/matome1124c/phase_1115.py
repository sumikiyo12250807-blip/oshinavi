# -*- coding: utf-8 -*-
# 101.8 と 135.8 のどちらが曲の拍か：12 秒ごとのスネア・キックの最良の位相と当たりを並べる（位相が揃う方が本物）
import io
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = io.open(D + 'tempo_fine.py', encoding='utf-8').read()
src = src[:src.index("print('① 134.0BPM")]
G = {}
exec(compile(src, 'tf', 'exec'), G)
SN, K, T, fit = G['SN'], G['K'], G['T'], G['fit']
out = []
for bpm in (101.8, 101.9, 102.0, 135.8, 136.0):
    for name, env in (('snare', SN), ('kick', K)):
        row = []
        for a in range(2, 104, 12):
            s, ph = fit(env, bpm, a, a + 12, 0.002)
            row.append('%d:%.3f/%.1f' % (a, ph, s))
        out.append('%.1f %s %s' % (bpm, name, ' '.join(row)))
io.open(D + 'phase_1115.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
