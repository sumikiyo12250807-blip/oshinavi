# -*- coding: utf-8 -*-
# g5・g6 の上 140 行の「濃い点（alpha>120）の数と左右の端」を並べる＝くつと頭の切れ目を探す
import io
import numpy as np
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
out = []
for n in ('g5', 'g6'):
    a = np.asarray(Image.open(D + n + '.png').convert('RGBA'))[:, :, 3]
    out.append('== %s %s' % (n, a.shape))
    for y in range(0, 140, 4):
        xs = np.where(a[y] > 120)[0]
        out.append('%3d %4d %s' % (y, len(xs), (xs.min(), xs.max()) if len(xs) else '-'))
io.open(D + 'rows_g56.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
