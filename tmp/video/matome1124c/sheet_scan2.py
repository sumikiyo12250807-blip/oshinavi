# -*- coding: utf-8 -*-
# 列ごとに、行の前景の量が少ない帯（上下の人の切れ目）を探す
import io
import numpy as np
import cv2
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
a = np.asarray(Image.open(D + 'sheet.png').convert('RGB')).astype(int)
H, W = a.shape[:2]
neu = (a.max(axis=2) - a.min(axis=2) < 10)
lum = a.sum(axis=2) / 3
fg = (~(neu & (lum >= 225))).astype(np.uint8)
fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
out = io.open(D + 'sheet_scan2.txt', 'w', encoding='utf-8')
for name, (x0, x1) in (('左', (110, 480)), ('中', (555, 1010)), ('右', (990, 1430))):
    r = fg[:, x0:x1].sum(axis=1)
    out.write('== %s 列 %d-%d\n' % (name, x0, x1))
    for y0 in range(280, 760, 4):
        out.write('%d:%d ' % (y0, r[y0:y0 + 4].sum() // 4))
    out.write('\n')
out.close()
