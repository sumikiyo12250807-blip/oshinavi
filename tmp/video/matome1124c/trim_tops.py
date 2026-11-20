# -*- coding: utf-8 -*-
# 下の段（p4〜p9）の頭のてっぺんに残った上の段の靴の底を消す：上の端 40px のうち、ピンクの髪の色（R>140 かつ R>G+30）でない所を透明に
import numpy as np
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
for k in range(4, 10):
    p = D + 'p%d.png' % k
    a = np.asarray(Image.open(p).convert('RGBA')).copy()
    top = a[:40]
    R, G = top[:, :, 0].astype(int), top[:, :, 1].astype(int)
    hair = (R > 140) & (R > G + 30)
    top[:, :, 3] = np.where(hair, top[:, :, 3], 0)
    a[:40] = top
    im = Image.fromarray(a)
    bb = im.getbbox()
    im.crop(bb).save(p)
