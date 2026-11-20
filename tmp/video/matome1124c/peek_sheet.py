# -*- coding: utf-8 -*-
# 市松模様の2色と升目の大きさを測る（左上の何も描かれていない所）
import sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from PIL import Image
a = np.asarray(Image.open('C:/Users/user/oshinavi/tmp/video/matome1124c/sheet.png').convert('RGB')).astype(int)
for (x0, y0, x1, y1) in ((0, 0, 60, 400), (1200, 0, 1254, 400), (420, 440, 520, 470)):
    r = a[y0:y1, x0:x1]
    lum = r.mean(axis=2).round().astype(int)
    h = np.bincount(lum.ravel(), minlength=256)
    top = np.argsort(h)[::-1][:6]
    print('box', (x0, y0, x1, y1), 'lum top', [(int(v), int(h[v])) for v in top], 'chroma max', int((r.max(axis=2) - r.min(axis=2)).max()))
row = a[200, 0:60].mean(axis=1).round().astype(int)
print('row200', list(row))
col = a[0:80, 20].mean(axis=1).round().astype(int)
print('col20', list(col))
