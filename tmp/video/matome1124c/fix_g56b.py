# -*- coding: utf-8 -*-
# g5・g6：上の子のくつ（上の幅 40px ほどの帯）を消す＝g5 は上 35 行、g6 は上 27 行を透明に → 切り詰める
import numpy as np
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
for n, cut in (('g5', 35), ('g6', 27)):
    a = np.asarray(Image.open(D + n + '.png').convert('RGBA')).copy()
    a[:cut, :, 3] = 0
    ys, xs = np.where(a[:, :, 3] > 20)
    Image.fromarray(a).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(D + n + '.png')
