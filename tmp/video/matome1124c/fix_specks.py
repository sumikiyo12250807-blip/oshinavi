# -*- coding: utf-8 -*-
# 切り抜きの手直し（目で見て決めた範囲）：上の段の子のくつ底の暗いかけらが下の段の子の頭に残った所を消す（暗い画素だけ）
import numpy as np
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
FIX = {'c4': [(104, 0, 126, 8)], 'c6': [(155, 0, 182, 8)], 'c9': [(122, 2, 148, 12)]}
for nm, rects in FIX.items():
    im = np.asarray(Image.open(D + nm + '.png').convert('RGBA')).copy()
    lum = im[:, :, :3].astype(int).mean(axis=2)
    n = 0
    for x0, y0, x1, y1 in rects:
        sl = (slice(y0, y1), slice(x0, x1))
        m = lum[sl] < 110
        n += int((m & (im[sl][:, :, 3] > 0)).sum())
        a = im[sl][:, :, 3]
        a[m] = 0
        im[y0:y1, x0:x1, 3] = a
    Image.fromarray(im).save(D + nm + '.png')
    print(nm, n)
