# -*- coding: utf-8 -*-
# a4（エルフの弓）・b5（森の鹿の子）の下に、下の段の子の縁取りの線が細く残った（本体と薄くつながっている）
#   並べた絵で足（ブーツ・裾・鹿の足）の下端を目で決めて、その下を消す（a4＝318 行・b5＝322 行）
import io
import numpy as np
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
CUT = {'a4': 318, 'b5': 322}
out = []
for nm, cut in CUT.items():
    a = np.asarray(Image.open(D + 'poses/%s.png' % nm)).copy()
    a[cut:, :, 3] = 0
    al = a[:, :, 3]
    ys, xs = np.where(al > 20)
    bb = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    Image.fromarray(a).crop(bb).save(D + 'poses/%s.png' % nm)
    out.append('%s %d 行で切った 新しい大きさ %s' % (nm, cut, (bb[2] - bb[0], bb[3] - bb[1])))
io.open(D + 'clean_stray14.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
