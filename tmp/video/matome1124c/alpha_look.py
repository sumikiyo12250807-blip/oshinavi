# -*- coding: utf-8 -*-
# シートの透け具合を見る（四隅・全体の alpha）と、alpha の濃い所の行・列の切れ目
import io
import numpy as np
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
im = Image.open(D + 'sheet_a.png')
a = np.asarray(im)[:, :, 3].astype(int)
L = ['alpha 0 の割合 %.2f / 255 の割合 %.2f' % ((a == 0).mean(), (a == 255).mean())]
for name, ax in (('行', 1), ('列', 0)):
    prof = (a > 40).sum(axis=ax)
    gaps = [i for i in range(len(prof)) if prof[i] < 3]
    runs, s = [], None
    for i in range(len(prof)):
        g = prof[i] < 3
        if g and s is None: s = i
        if not g and s is not None:
            runs.append((s, i - 1)); s = None
    if s is not None: runs.append((s, len(prof) - 1))
    L.append('%s のすき間 %s' % (name, runs))
    L.append('%s の最小（中央付近）: %s' % (name, sorted(range(300, 960), key=lambda i: prof[i])[:6]))
io.open(D + 'alpha_look.txt', 'w', encoding='utf-8').write('\n'.join(L))
