# -*- coding: utf-8 -*-
# b5/b8 のすき間：行ごとに x520〜770 で アルファ≥128 の画素の数と範囲
import sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from PIL import Image
A = np.asarray(Image.open('C:/Users/user/oshinavi/tmp/video/matome1124c/sheet_b.png'))[:, :, 3]
for y in range(770, 880, 2):
    r = A[y, 514:766]
    xs = np.where(r >= 128)[0] + 514
    segs = []
    if len(xs):
        st = xs[0]
        for a, b in zip(xs[:-1], xs[1:]):
            if b != a + 1:
                segs.append((st, a)); st = b
        segs.append((st, xs[-1]))
    print(y, len(xs), segs)
