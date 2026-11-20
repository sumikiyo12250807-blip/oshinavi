# -*- coding: utf-8 -*-
# 2枚のシートの透明度（alpha）が本当に人の形になっているか数える
import io
import numpy as np
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
out = []
for s in ('sheet.png', 'sheet2.png'):
    a = np.asarray(Image.open(D + s).convert('RGBA'))[:, :, 3]
    out.append('%s 透明0の割合 %.3f  255の割合 %.3f  中間 %.3f  隅(0,0)=%d (768,512)=%d' % (
        s, (a == 0).mean(), (a == 255).mean(), ((a > 0) & (a < 255)).mean(), a[0, 0], a[512, 768]))
    Image.fromarray(a).resize((384, 256)).save(D + 'alpha_%s' % s)
io.open(D + 'astat.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
