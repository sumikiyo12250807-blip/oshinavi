# -*- coding: utf-8 -*-
# 拍＝tempo_check.py の測り（キック 67.0／134.0 BPM・位相 0.224／スネア 134.2）の等間隔の格子（寄せない）＝matome1028o/grid_beats.py の形
#   67 は半分の速さ＝134 BPM を拍にする。位相はキックの 0.224 秒（全帯域の 0.786 は裏拍のスネア）
import io, json
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
T = json.load(io.open(D + 'tempo_check.json'))
kb = next(k for k in T['kick'] if abs(k[1] - 134.0) < 0.5)
bpm, ph = kb[1], kb[2]
P = 60 / bpm
beats, t = [], ph
while t < 97.0:
    beats.append(round(t, 3)); t += P
json.dump({'bpm': bpm, 'beats': beats}, io.open(D + 'beats.json', 'w'))
print('bpm', bpm, 'phase', ph, 'beats', len(beats), beats[:5])
