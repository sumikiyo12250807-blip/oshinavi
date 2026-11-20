# -*- coding: utf-8 -*-
# g5：頭の上に残った黒いくつ底の点（上 20 行・x 135〜190 の暗い点）を消す
import numpy as np
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
a = np.asarray(Image.open(D + 'g5.png').convert('RGBA')).copy()
rgb = a[:20, 135:190, :3].astype(int)
dark = rgb.sum(axis=2) < 230
sub = a[:20, 135:190, 3]
sub[dark] = 0
a[:20, 135:190, 3] = sub
ys, xs = np.where(a[:, :, 3] > 20)
Image.fromarray(a).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(D + 'g5.png')
big = Image.fromarray(a).crop((0, 0, a.shape[1], 120)).resize((a.shape[1] * 3, 360))
bg = Image.new('RGBA', big.size, (120, 120, 120, 255)); bg.alpha_composite(big)
bg.convert('RGB').save(D + 'top_g5.png')
