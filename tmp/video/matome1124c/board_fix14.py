# -*- coding: utf-8 -*-
# board.py と clips_1115.py の秒を 11/14（67.6 秒）用に差し替える
import io
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
b = io.open(D + 'board.py', encoding='utf-8').read()
old = "[1.0, 5.0, 9.0, 15.5, 20.5, 26.5, 32.0, 38.0, 44.0, 49.5, 55.5, 61.0, 67.0, 72.5, 78.5, 84.0, 89.0, 93.0, 97.5, 101.5, 104.5, 107.3, 108.8]   # 11/15：15着＋タップ＋締め＋後奏・最後の2秒"
assert old in b
b = b.replace(old, "[2.5, 7.0, 12.0, 16.5, 21.5, 26.0, 31.0, 35.5, 40.5, 45.0, 50.0, 54.0, 57.5, 61.0, 63.5, 65.6]   # 11/14：10着＋タップ2つ＋締め＋後奏・最後の2秒（65.6）")
io.open(D + 'board.py', 'w', encoding='utf-8').write(b)
c = io.open(D + 'clips_1115.py', encoding='utf-8').read()
old = "(('clip_a', 9.5, 24.5), ('clip_b', 95.0, 109.3))"
assert old in c
c = c.replace(old, "(('clip_a', 9.0, 24.0), ('clip_b', 52.0, 67.6))")
io.open(D + 'clips_1114.py', 'w', encoding='utf-8').write(c.replace('clips_1115', 'clips_1114'))
print('ok')
