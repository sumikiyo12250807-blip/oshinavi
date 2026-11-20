# -*- coding: utf-8 -*-
# g5・g6：くつの底のかけら（上 12 行の右寄り）だけ消す
import numpy as np
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
for n, x0, rows in (('g5', 130, 12), ('g6', 140, 12)):
    a = np.asarray(Image.open(D + n + '.png').convert('RGBA')).copy()
    a[:rows, x0:, 3] = 0
    ys, xs = np.where(a[:, :, 3] > 20)
    Image.fromarray(a).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(D + n + '.png')
    big = Image.fromarray(a).crop((0, 0, a.shape[1], 120)).resize((a.shape[1] * 3, 360))
    bg = Image.new('RGBA', big.size, (120, 120, 120, 255)); bg.alpha_composite(big)
    bg.convert('RGB').save(D + 'top_%s.png' % n)
