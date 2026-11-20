# -*- coding: utf-8 -*-
# 11/16 TikTok スポーツ（75.6秒）：tempo_check 1位＝96.6BPM（スネア 3.80）→ 96.0〜97.2 を 0.05 刻みでスネアに当て直し、10秒ごとの位相を見る → beats.json
import io, json
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
s = io.open(D + 'beats_1114.py', encoding='utf-8').read()
s = s.replace('END = 67.5', 'END = 75.5').replace('np.arange(100.5, 101.51, 0.05)', 'np.arange(96.0, 97.21, 0.05)')
s = s.replace('fit(SN, b, 1, 66, 0.002)', 'fit(SN, b, 1, 74, 0.002)').replace('range(0, 70, 10)', 'range(0, 80, 10)').replace("beats_1114.txt", "beats_1116.txt")
exec(compile(s, 'beats_1116', 'exec'))
