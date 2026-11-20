# -*- coding: utf-8 -*-
# 11/17 TikTok J-POP（60.9秒）：tempo_check 1位＝75.0BPM（スネア 4.78・2位 150＝倍）→ 74.5〜75.5 を 0.02 刻みでスネアに当て直し、10秒ごとの位相を見る → beats.json
#   150 の格子は 0.4 秒ごとに弾む＝せかせか。75（0.8 秒）＝スネアの 2・4 拍に乗る落ち着いた弾み
import io
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
s = io.open(D + 'beats_1114.py', encoding='utf-8').read()
for a, b in (('END = 67.5', 'END = 60.8'), ('np.arange(100.5, 101.51, 0.05)', 'np.arange(74.5, 75.51, 0.02)'),
             ('fit(SN, b, 1, 66, 0.002)', 'fit(SN, b, 1, 59.5, 0.002)'), ("beats_1114.txt", "beats_1117.txt")):
    assert a in s, a
    s = s.replace(a, b)
exec(compile(s, 'beats_1117', 'exec'))
