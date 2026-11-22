# -*- coding: utf-8 -*-
# 3コマ目（musical_move3_1126.png）は背景が「透明の市松模様」を描いた不透明の絵だった＝端からつながった白・薄いグレー（色みのない明るい画素）を透明にする → Downloads/musical_move3_1126t.png
import numpy as np
from PIL import Image
from scipy import ndimage
src = 'C:/Users/user/Downloads/musical_move3_1126.png'
im = np.array(Image.open(src).convert('RGBA')).astype(np.int16)
r, g, b = im[:, :, 0], im[:, :, 1], im[:, :, 2]
mx = np.maximum(np.maximum(r, g), b); mn = np.minimum(np.minimum(r, g), b)
light = (mn >= 200) & (mx - mn <= 18)
lab, n = ndimage.label(light)
edge = set(np.unique(np.concatenate([lab[0, :], lab[-1, :], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(edge))
# 背景と接する1画素のふちも少し落とす（市松のにじみ）
bg2 = ndimage.binary_dilation(bg, iterations=1) & light
out = im.astype(np.uint8)
out[:, :, 3] = np.where(bg | bg2, 0, 255).astype(np.uint8)
Image.fromarray(out).save('C:/Users/user/Downloads/musical_move3_1126t.png')
print('背景にした画素の割合 %.3f' % (bg | bg2).mean())
