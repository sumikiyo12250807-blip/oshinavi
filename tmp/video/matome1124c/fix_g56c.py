# -*- coding: utf-8 -*-
# g5・g6：上の端に残ったくつの底を消す＝上から、その行の点（alpha>60）が 50 未満の行が続く間は透明に → そのあと 4 行ぶん余分に、幅の細い所（x の中央 ±40 の外は残す）
import io
import numpy as np
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
log = []
for n in ('g5', 'g6'):
    a = np.asarray(Image.open(D + n + '.png').convert('RGBA')).copy()
    y = 0
    while y < 60 and (a[y, :, 3] > 60).sum() < 50:
        y += 1
    log.append('%s 上から %d 行を透明に' % (n, y))
    a[:y, :, 3] = 0
    ys, xs = np.where(a[:, :, 3] > 20)
    Image.fromarray(a).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(D + n + '.png')
io.open(D + 'fix_g56c.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
