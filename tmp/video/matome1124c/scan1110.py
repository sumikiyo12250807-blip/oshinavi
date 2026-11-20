# -*- coding: utf-8 -*-
# 11/10 シート（1536×1024・白地）の地の色と、3×3 の各マスの絵の外接矩形を測る → scan1110.txt
import io
import numpy as np
import cv2
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
a = np.asarray(Image.open(D + 'sheet.png').convert('RGB')).astype(int)
H, W = a.shape[:2]
neu = (a.max(axis=2) - a.min(axis=2) < 8)
lum = a.sum(axis=2) / 3
out = []
# 地の色の分布（四隅 60×60）
for (y, x) in ((0, 0), (0, W - 60), (H - 60, 0), (H - 60, W - 60)):
    p = lum[y:y + 60, x:x + 60]
    out.append('隅 %d,%d lum %.1f〜%.1f 中性 %.2f' % (x, y, p.min(), p.max(), neu[y:y + 60, x:x + 60].mean()))
bg = neu & (lum >= 238)
fg = (~bg).astype(np.uint8)
fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
# 行と列の切れ目（前景が無い帯）
col = fg.sum(axis=0)
row = fg.sum(axis=1)
def gaps(v, n):
    g, s = [], None
    for i, x in enumerate(v):
        if x <= 2 and s is None:
            s = i
        if x > 2 and s is not None:
            g.append((s, i)); s = None
    if s is not None:
        g.append((s, n))
    return g
out.append('列のすき間 %s' % gaps(col, W))
out.append('行のすき間 %s' % gaps(row, H))
n, lab, st, cen = cv2.connectedComponentsWithStats(fg, 8)
big = [(st[j, 4], tuple(st[j, :4]), tuple(int(c) for c in cen[j])) for j in range(1, n) if st[j, 4] > 300]
big.sort(key=lambda x: (x[2][1] // 340, x[2][0]))
for area, (x, y, w, h), c in big:
    out.append('塊 面積 %d 箱 (%d,%d,%d,%d) 中心 %s' % (area, x, y, x + w, y + h, c))
io.open(D + 'scan1110.txt', 'w', encoding='utf-8').write('\n'.join(out))
