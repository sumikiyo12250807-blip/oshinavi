# -*- coding: utf-8 -*-
import numpy as np
from PIL import Image
for f in ('sheetB.png', 'sheetA.png'):
    im = Image.open('C:/Users/user/oshinavi/tmp/video/shuyaku1113/' + f)
    a = np.asarray(im.convert('RGBA'))[:, :, 3]
    print(f, im.size, im.mode, '0の割合 %.2f 255 %.2f' % ((a == 0).mean(), (a == 255).mean()))
