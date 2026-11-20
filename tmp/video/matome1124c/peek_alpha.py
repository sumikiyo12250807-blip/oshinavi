# -*- coding: utf-8 -*-
# 2枚のシートのアルファを調べる：値の分布・強い前景の塊（コマ）の外接矩形・行/列の投影の谷
import sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np, cv2
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
for f in ('sheet_a.png', 'sheet_b.png'):
    im = np.asarray(Image.open(D + f))
    a = im[:, :, 3]
    print('==', f, im.shape)
    h = np.histogram(a, bins=[0, 1, 16, 64, 128, 200, 250, 256])[0]
    print('alpha hist 0|1-15|16-63|64-127|128-199|200-249|250+', h.tolist())
    rgb = im[:, :, :3].astype(int)
    lowa = (a > 0) & (a < 200)
    sat = rgb.max(axis=2) - rgb.min(axis=2)
    print('半透明の画素の彩度の中央値', float(np.median(sat[lowa])) if lowa.any() else None)
    for th in (128, 230):
        m = (a >= th).astype(np.uint8)
        n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
        big = sorted([tuple(int(v) for v in st[j]) for j in range(1, n) if st[j, 4] > 3000], key=lambda s: (s[1] // 300, s[0]))
        print('th', th, '大きい塊', len(big))
        for s in big:
            print('   x%d y%d w%d h%d area%d' % s)
    m = (a >= 128)
    col = m.sum(axis=0)
    row = m.sum(axis=1)
    print('列の投影 0 の区間', [(i, j) for i, j in zip(*[np.where(np.diff(np.r_[0, (col == 0).astype(int), 0]) == v)[0] for v in (1, -1)]) if j - i > 5])
    print('行の投影の小さい所', ' '.join('%d:%d' % (y, row[y]) for y in range(0, len(row), 10)))
