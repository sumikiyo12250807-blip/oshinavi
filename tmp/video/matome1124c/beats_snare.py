# -*- coding: utf-8 -*-
# 拍を作る（10/28 すちこ「リズムが結局ぜんぜんあってない」＝キックに当てた格子は目で見て合わなかった → 今回はスネアに当てる）
#   ①96.0〜98.0BPM を 0.02 刻みでスネア（150〜4000Hz）に当てて BPM を決める
#   ②その BPM で 4 秒の窓ごとにスネアへ位相を当て、巻き戻しをほどいて3窓の中央値でならす（grid_beats2 と同じ作り）
#   ③10秒ごとの当たりを出す → beats.json（bpm・beats）
import io, json, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = io.open(D + 'tempo_fine.py', encoding='utf-8').read()
src = src[:src.index("print('① 134.0BPM")]
G = {}
exec(compile(src, 'tf', 'exec'), G)
SN, K, T, fit = G['SN'], G['K'], G['T'], G['fit']
END = 58.0   # 11/10 お笑い：曲 58.8 秒・キック／全帯域 133.2 が上位      # 11/6 お笑い：曲 66.3 秒・tempo_check はスネア・キック・全帯域とも 100.0 が1位   # 11/5 お笑い：曲 93.6 秒・tempo_check はスネア・キックとも 149.0 が1位      # 11/1 お笑い：曲 87.2 秒・tempo_check はキック 62.4/124.8・スネア 187.2/93.6（3連のスイング）＝前奏4小節が 7.6 秒＝124.8BPM が本当の拍
sc = sorted(((fit(SN, b, 1, END, 0.002) + (b,)) for b in np.arange(132.9, 133.31, 0.02)), reverse=True)[:5]
out = ['BPM候補（スネア） ' + ' '.join('%.2f:%.2f@%.3f' % (b, s, p) for s, p, b in sc)]
BPM = float(sc[0][2])
P = 60 / BPM
W = 4.0
cs, phs = [], []
for a in np.arange(0, END - 2, W):
    s, ph = fit(SN, BPM, a, a + W, 0.002)
    cs.append(a + W / 2); phs.append(ph)
un = [phs[0]]
for p in phs[1:]:
    q = p
    while q - un[-1] > P / 2: q -= P
    while q - un[-1] < -P / 2: q += P
    un.append(q)
sm = [float(np.median(un[max(0, i - 1):i + 2])) for i in range(len(un))]
# 10/31：窓の位相は 0.364〜0.378 にそろって流れていない。前奏（2秒）と 10・34 秒の窓だけ半拍ずれた（裏を拾った）
#   ＝3窓の中央値でも頭の拍がゆれた（間隔 0.659〜0.686）→ 全部の窓の中央値1つの等間隔の格子にする
sm = [float(np.median(un))] * len(un)
# 11/3：この曲は位相が 40 秒の 0.30 から 106 秒の −0.19 まで流れた（Suno のテンポが少し揺れる）＝1本の格子では後半が半拍ずれる
#   → 5窓（20秒）の中央値でならして位相を追う（26・30 秒の窓は裏拍を拾った 0.525 ＝中央値で落ちる）
sm = [float(np.median(un[max(0, i - 2):i + 3])) for i in range(len(un))]
# 11/6：位相は 14〜62 秒で 0.284〜0.290 にそろう（前奏の 2・6・10 秒と 22 秒の窓だけ裏拍 0.56〜0.59／−0.01）＝1本の格子に戻す
sm = [float(np.median(un[max(0, i - 2):i + 3])) for i in range(len(un))]   # 11/7 位相が流れる曲＝5窓の中央値で追う
out.append('窓の位相 ' + ' '.join('%.0f:%.3f' % (c, p) for c, p in zip(cs, un)))
beats, n = [], 0
while True:
    t = n * P + float(np.interp(n * P, cs, sm))
    if t > END: break
    if t >= 0: beats.append(round(t, 3))
    n += 1
iv = np.diff(beats)
out.append('拍 %d 間隔 %.3f〜%.3f' % (len(beats), iv.min(), iv.max()))


def strength(env, bs):
    idx = np.clip(np.searchsorted(T, bs), 0, len(env) - 1)
    return float(env[idx].mean() / env.mean())
out.append('当たり スネア %.2f キック %.2f' % (strength(SN, beats), strength(K, beats)))
for a in range(0, 120, 10):
    nn = [b for b in beats if a <= b < a + 10]
    out.append('  %2d〜%2d秒 スネア %.2f キック %.2f' % (a, a + 10, strength(SN, nn), strength(K, nn)))
json.dump({'bpm': BPM, 'beats': beats}, io.open(D + 'beats.json', 'w'))
io.open(D + 'beats_snare.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
