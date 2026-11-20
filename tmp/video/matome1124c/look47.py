# -*- coding: utf-8 -*-
import io, re
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
t = io.open(D + 'cut9_w.txt', encoding='utf-8').read()
t = re.sub(r'w4 大きさ .*\n', 'w4 大きさ (482, 335) シート上 (41, 338, 523, 673)\n', t)
t = re.sub(r'w7 大きさ .*\n', 'w7 大きさ (447, 351) シート上 (48, 673, 495, 1024)\n', t)
io.open(D + 'cut9_w.txt', 'w', encoding='utf-8').write(t)
exec(compile(io.open(D + 'look_n.py', encoding='utf-8').read(), 'look_n', 'exec'))
