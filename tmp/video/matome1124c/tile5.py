# -*- coding: utf-8 -*-
# frames/h_*.png を横に並べて小さく → art/tile.png
import glob
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
fs = sorted(glob.glob(D + 'frames/h_*.png'))
W, H = 432, 768
o = Image.new('RGB', (len(fs) * (W + 8), H), (0, 0, 0))
for i, f in enumerate(fs):
    o.paste(Image.open(f).convert('RGB').resize((W, H)), (i * (W + 8), 0))
o.save(D + 'art/tile.png')
