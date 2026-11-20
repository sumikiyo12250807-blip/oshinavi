# -*- coding: utf-8 -*-
import sys
import numpy as np
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
a = np.asarray(Image.open(D + 'sheet.png'))[:, :, 3]
print('alpha min', a.min(), 'max', a.max(), 'mean', a.mean(), 'frac<10', (a < 10).mean(), 'frac>245', (a > 245).mean())
# 行・列ごとの不透明率
print('rows', [round(float((a[y] > 128).mean()), 2) for y in range(0, 1024, 32)])
print('cols', [round(float((a[:, x] > 128).mean()), 2) for x in range(0, 1536, 48)])
