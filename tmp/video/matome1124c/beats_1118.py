# -*- coding: utf-8 -*-
# 11/18 舞台・トークショー（76.1秒）：tempo_check スネア1位＝60.0BPM（3.72・2位 119.8＝倍）→ 59.5〜60.5 を 0.02 刻みでスネアに当て直し、10秒ごとの位相を見る → beats.json
#   120 の格子は 0.5 秒ごとに弾む＝せかせか。60（1.0 秒）＝落ち着いた弾み（11/17 の 75 と同じ考え）
import io
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
s = io.open(D + 'beats_1114.py', encoding='utf-8').read()
for a, b in (('END = 67.5', 'END = 75.8'), ('np.arange(100.5, 101.51, 0.05)', 'np.arange(59.5, 60.51, 0.02)'),
             ('fit(SN, b, 1, 66, 0.002)', 'fit(SN, b, 1, 74.5, 0.002)'), ("beats_1114.txt", "beats_1118.txt")):
    assert a in s, a
    s = s.replace(a, b)
exec(compile(s, 'beats_1118', 'exec'))
