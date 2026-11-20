# -*- coding: utf-8 -*-
# シートの alpha を白黒で・シートを濃紺の地に重ねた絵 → art/alpha.png・art/on_navy.png
import numpy as np
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
im = Image.open(D + 'sheet.png').convert('RGBA')
a = np.asarray(im)[:, :, 3]
Image.fromarray(a).save(D + 'art/alpha.png')
bg = Image.new('RGBA', im.size, (20, 15, 50, 255))
bg.alpha_composite(im)
bg.convert('RGB').save(D + 'art/on_navy.png')
h = np.histogram(a, bins=[0, 10, 40, 80, 120, 160, 200, 240, 256])[0]
print('hist', list(h))
