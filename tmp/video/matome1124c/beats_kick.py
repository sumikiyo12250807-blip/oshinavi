# -*- coding: utf-8 -*-
# 11/1 お笑いまとめにも主役の歌（matome1101s/beats_kick.py）と同じ拍の作り直し
#   phase_check.txt：スネアは窓によって ±143ms（＝1拍の1/3＝スイングの3連の裏）に飛ぶ＝スネアに当てると裏を拾う
#   キックは全部の窓でほぼ同じ位相（0〜+20ms・後半だけ +20〜+40ms へ少しずつ遅れる）＝キックを拍の頭にする
#   140.02BPM の格子に、4秒の窓ごとのキックのずれ（±60ms を超える窓は外れ＝隣の値）を5窓の中央値でならして足す（grid_beats2 の形）
#   → beats.json（もとの beats.json は beats_snare.json に残す）
import io, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = io.open(D + 'tempo_fine.py', encoding='utf-8').read()
src = src[:src.index("print('① 134.0BPM")]
G = {}
exec(compile(src, 'tf', 'exec'), G)
SN, K, T, fit = G['SN'], G['K'], G['T'], G['fit']
if not os.path.exists(D + 'beats_snare.json'):
    os.replace(D + 'beats.json', D + 'beats_snare.json')
B0 = json.load(io.open(D + 'beats_snare.json'))
BPM = B0['bpm']
P = 60 / BPM
g0 = B0['beats'][0] % P
END, W = 67.0, 4.0
cs, dv = [], []
for a in np.arange(0, END - 1, W):
    s, ph = fit(K, BPM, a, a + W, 0.001)
    d = (ph - g0) % P
    d = d - P if d > P / 2 else d
    cs.append(a + W / 2); dv.append(d)
dv = np.array(dv)
bad = np.abs(dv) > 0.060
good = dv.copy()
for i in np.where(bad)[0]:
    nb = [dv[j] for j in range(max(0, i - 3), min(len(dv), i + 4)) if not bad[j]]
    good[i] = float(np.median(nb)) if nb else 0.0
sm = np.array([float(np.median(good[max(0, i - 2):i + 3])) for i in range(len(good))])
beats, n = [], 0
while True:
    t0 = g0 + n * P
    if t0 > END:
        break
    t = t0 + float(np.interp(t0, cs, sm))
    if t >= 0:
        beats.append(round(t, 4))
    n += 1


def strength(env, bs):
    idx = np.clip(np.searchsorted(T, bs), 0, len(env) - 1)
    return float(env[idx].mean() / env.mean())


out = ['BPM %.2f 位相 %.3f（スネアの格子と同じ）' % (BPM, g0),
       '窓ごとのキックのずれ(ms) ' + ' '.join('%.0f:%+.0f%s' % (c, d * 1000, '×' if b else '') for c, d, b in zip(cs, dv, bad)),
       'ならした足し分(ms) ' + ' '.join('%.0f:%+.0f' % (c, d * 1000) for c, d in zip(cs, sm)),
       '拍 %d 間隔 %.4f〜%.4f' % (len(beats), np.diff(beats).min(), np.diff(beats).max()),
       '当たり 新 キック %.2f スネア %.2f ／ 旧 キック %.2f スネア %.2f' % (strength(K, beats), strength(SN, beats), strength(K, B0['beats']), strength(SN, B0['beats']))]
for a in range(0, 90, 10):
    nn = [b for b in beats if a <= b < a + 10]
    oo = [b for b in B0['beats'] if a <= b < a + 10]
    out.append('  %3d〜%3d秒 キック 新 %.2f 旧 %.2f' % (a, a + 10, strength(K, nn), strength(K, oo)))
json.dump({'bpm': BPM, 'beats': beats}, io.open(D + 'beats.json', 'w'))
io.open(D + 'beats_kick.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
