# -*- coding: utf-8 -*-
# 拍を作り直す（すちこ「音楽にキャラクターのリズムがあってない」）
#   第1版＝134.0BPM の1本の格子。10秒ごとに測ると、キックとの位相が最大0.2秒（約半拍）流れていた（tempo_fine.py）
#   ①4秒の窓ごとに、134.2BPM の格子をキック（30〜150Hz）に当てて位相を取る（隣の窓とつながるよう周期ぶんの巻き戻しをほどく）
#   ②位相を3窓の中央値でならして、拍の時刻を「その時刻の位相」で作る＝間隔はなめらかに変わるだけ（1拍ずつ寄せない＝10/20 の失敗を避ける）
#   ③点検＝できた拍の上のキックの強さを、第1版の格子と比べる
import io, json, runpy, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = io.open(D + 'tempo_fine.py', encoding='utf-8').read()
src = src[:src.index("print('① 134.0BPM")]
G = {}
exec(compile(src, 'tf', 'exec'), G)
K, T, fit = G['K'], G['T'], G['fit']
BPM = 134.2
P = 60 / BPM
W = 4.0
cs, phs = [], []
for a in np.arange(0, 92, W):
    s, ph = fit(K, BPM, a, a + W, 0.002)
    cs.append(a + W / 2); phs.append(ph)
# 巻き戻しをほどく（隣との差が半周期を超えたら1周期ずらす）
un = [phs[0]]
for p in phs[1:]:
    q = p
    while q - un[-1] > P / 2: q -= P
    while q - un[-1] < -P / 2: q += P
    un.append(q)
sm = [float(np.median(un[max(0, i - 1):i + 2])) for i in range(len(un))]   # 3窓の中央値（5窓は当たり 3.40＜3窓 4.03＝裏に入った所もキックについていく方が合う）
print('窓の位相', ' '.join('%.0f:%.3f' % (c, p) for c, p in zip(cs, un)))
print('ならした', ' '.join('%.3f' % p for p in sm))
beats = []
n = 0
while True:
    t0 = n * P
    ph = float(np.interp(t0, cs, sm))
    t = t0 + ph
    if t > 96.0: break
    if t >= 0: beats.append(round(t, 3))
    n += 1
iv = np.diff(beats)
print('拍', len(beats), '間隔 最小 %.3f 最大 %.3f' % (iv.min(), iv.max()))


def strength(bs):
    idx = np.clip(np.searchsorted(T, bs), 0, len(K) - 1)
    return float(K[idx].mean() / K.mean())
old = json.load(io.open(D + 'beats.json'))['beats']
print('キックの当たり 第1版 %.2f → 作り直し %.2f' % (strength(old), strength(beats)))
for a in range(0, 90, 10):
    o = [b for b in old if a <= b < a + 10]; nn = [b for b in beats if a <= b < a + 10]
    print('  %2d〜%2d秒 第1版 %.2f 作り直し %.2f' % (a, a + 10, strength(o), strength(nn)))
json.dump({'bpm': BPM, 'beats': beats}, io.open(D + 'beats2.json', 'w'))
