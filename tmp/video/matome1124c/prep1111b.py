# -*- coding: utf-8 -*-
# beat_char の MAXH を今日の名前（w/m/s/t）で数える・前奏の塊は「歌い出しが 1 秒より後の時だけ」入れる（今日は 0.5 秒で歌い出す）
import io
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
bc = io.open(D + 'beat_char.py', encoding='utf-8').read()
a = "poses/[rn][1-9].png'))"
assert a in bc
bc = bc.replace(a, "poses/[wmst][1-9].png'))   # 11/11 パリコレの子", 1)
io.open(D + 'beat_char.py', 'w', encoding='utf-8').write(bc)
ms = io.open(D + 'make_spec.py', encoding='utf-8').read()
a = "chunks.insert(0, {'show': 0.3, 'hide': chunks[0]['show'],"
assert a in ms
ms = ms.replace(a, "if chunks[0]['show'] > 1.0:   # 11/11 歌い出し 0.5 秒＝前奏の塊は要らない（最初の塊が 0.17 秒から出ている）\n    chunks.insert(0, {'show': 0.3, 'hide': chunks[0]['show'],", 1)
io.open(D + 'make_spec.py', 'w', encoding='utf-8').write(ms)
print('ok')
