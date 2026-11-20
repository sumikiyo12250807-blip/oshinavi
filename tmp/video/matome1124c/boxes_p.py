# -*- coding: utf-8 -*-
# 11/11 パリコレの子（3×3）：段の切れ目2つと、段ごとの列の切れ目（前景の少ない所）→ boxes_p.txt
import io
import numpy as np
import cv2
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
a = np.asarray(Image.open(D + 'sheet.png').convert('RGB')).astype(int)
neu = (a.max(axis=2) - a.min(axis=2) < 10)
lum = a.sum(axis=2) / 3
fg = ~(neu & (lum >= 225))
fg = cv2.morphologyEx(fg.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)).astype(bool)
out = []
row = fg.sum(axis=1)
H, W = fg.shape
cuts_y = []
for c in (H // 3, 2 * H // 3):
    lo, hi = c - 80, c + 80
    y = lo + int(row[lo:hi].argmin())
    cuts_y.append(y)
    out.append('段の切れ目 %d（前景 %d）' % (y, row[y]))
    out.append('   %s' % ' '.join('%d:%d' % (yy, row[yy]) for yy in range(lo, hi, 8)))
bands = [(0, cuts_y[0]), (cuts_y[0], cuts_y[1]), (cuts_y[1], H)]
for name, (y0, y1) in zip(('上', '中', '下'), bands):
    col = fg[y0:y1].sum(axis=0)
    cuts = []
    for k in (1, 2):
        c = int(W * k / 3)
        lo, hi = c - 150, c + 150
        x = lo + int(col[lo:hi].argmin())
        cuts.append((x, int(col[x])))
    xs = np.where(col > 0)[0]
    out.append('%s y%d〜%d 前景の左端 %d 右端 %d 列の切れ目 %s' % (name, y0, y1, xs.min(), xs.max(), cuts))
io.open(D + 'boxes_p.txt', 'w', encoding='utf-8').write('\n'.join(out))
