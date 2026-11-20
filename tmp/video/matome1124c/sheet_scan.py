# -*- coding: utf-8 -*-
# シートの地（白と薄い灰の市松）でない所を前景として、9人の外接箱と、行・列の切れ目（前景の無い帯）を測る
import io, sys
import numpy as np
import cv2
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
a = np.asarray(Image.open(D + 'sheet.png').convert('RGB')).astype(int)
H, W = a.shape[:2]
neu = (a.max(axis=2) - a.min(axis=2) < 10)
lum = a.sum(axis=2) / 3
bg = neu & (lum >= 225)
out = io.open(D + 'sheet_scan.txt', 'w', encoding='utf-8')
vals, cnt = np.unique((lum[bg]).astype(int), return_counts=True)
top = sorted(zip(cnt, vals), reverse=True)[:6]
out.write('地の明るさ上位 %s\n' % top)
fg = (~bg).astype(np.uint8)
fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
rows = fg.sum(axis=1)
cols = fg.sum(axis=0)
out.write('行ごとの前景（0の帯）:\n')
z = [y for y in range(H) if rows[y] < 3]
# まとめて帯に
def bands(z):
    r = []
    for y in z:
        if r and y == r[-1][1] + 1:
            r[-1][1] = y
        else:
            r.append([y, y])
    return r
out.write('%s\n' % bands(z))
for name, (y0, y1) in (('上段', (0, 341)), ('中段', (341, 682)), ('下段', (682, 1024))):
    c = fg[y0:y1].sum(axis=0)
    out.write('%s 列の0帯 %s\n' % (name, bands([x for x in range(W) if c[x] < 3])))
dl = cv2.dilate(fg, np.ones((9, 9), np.uint8))
n, lab, st, cen = cv2.connectedComponentsWithStats(dl, 8)
for j in sorted(range(1, n), key=lambda j: -st[j, 4])[:20]:
    out.write('塊 x%d y%d w%d h%d 面積%d\n' % tuple(st[j]))
out.close()
