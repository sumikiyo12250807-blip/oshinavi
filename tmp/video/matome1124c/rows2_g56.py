# -*- coding: utf-8 -*-
import io
import numpy as np
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
out = []
for n in ('g5', 'g6'):
    a = np.asarray(Image.open(D + n + '.png').convert('RGBA'))[:, :, 3]
    out.append('== %s %s' % (n, a.shape))
    for y in range(0, 40):
        xs = np.where(a[y] > 60)[0]
        out.append('%3d %4d %s' % (y, len(xs), (int(xs.min()), int(xs.max())) if len(xs) else '-'))
io.open(D + 'rows2_g56.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
