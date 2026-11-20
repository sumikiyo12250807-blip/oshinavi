# -*- coding: utf-8 -*-
# 2枚目（歩く子・上5人／下4人）の段の切れ目と、段ごとの列の切れ目（前景の少ない所）を測る → boxes2.txt
import io
import numpy as np
import cv2
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
a = np.asarray(Image.open(D + 'sheet2.png').convert('RGB')).astype(int)
neu = (a.max(axis=2) - a.min(axis=2) < 10)
lum = a.sum(axis=2) / 3
fg = ~(neu & (lum >= 225))
fg = cv2.morphologyEx(fg.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)).astype(bool)
out = []
row = fg.sum(axis=1)
seg = row[420:560]
cut = 420 + int(seg.argmin())
out.append('段の切れ目 %d（前景 %d）' % (cut, seg.min()))
for name, y0, y1, n in (('上', 0, cut, 5), ('下', cut, a.shape[0], 4)):
    col = fg[y0:y1].sum(axis=0)
    W = a.shape[1]
    cuts = []
    for k in range(1, n):
        c = int(W * k / n)
        lo, hi = c - 110, c + 110
        x = lo + int(col[lo:hi].argmin())
        cuts.append((x, int(col[x])))
    xs = np.where(col > 0)[0]
    out.append('%s 前景の左端 %d 右端 %d 列の切れ目 %s' % (name, xs.min(), xs.max(), cuts))
    ys = np.where(fg[y0:y1].sum(axis=1) > 0)[0]
    out.append('   上端 %d 下端 %d' % (y0 + ys.min(), y0 + ys.max()))
io.open(D + 'boxes2.txt', 'w', encoding='utf-8').write('\n'.join(out))
