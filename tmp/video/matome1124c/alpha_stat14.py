# -*- coding: utf-8 -*-
import io
import numpy as np
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
out = []
for s in ('sheet.png', 'sheet2.png'):
    a = np.asarray(Image.open(D + s))[:, :, 3]
    out.append('%s alpha min %d max %d 透明(<10) %.1f%% 不透明(>245) %.1f%%' % (s, a.min(), a.max(), (a < 10).mean() * 100, (a > 245).mean() * 100))
io.open(D + 'alpha_stat14.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
