# -*- coding: utf-8 -*-
# frames/h_*.png を 8 枚ずつ縮めて並べる（自分で見る用）→ peek_1.png・peek_2.png
import glob
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
fs = sorted(glob.glob(D + 'frames/h_*.png'))
for k in range(0, len(fs), 8):
    part = fs[k:k + 8]
    g = Image.new('RGB', (270 * 4, 480 * 2 + 40), (0, 0, 0))
    d = ImageDraw.Draw(g)
    for i, f in enumerate(part):
        im = Image.open(f).convert('RGB').resize((270, 480))
        g.paste(im, ((i % 4) * 270, (i // 4) * 500 + 20))
        d.text(((i % 4) * 270 + 4, (i // 4) * 500 + 4), f[-11:-4], fill=(255, 255, 0))
    g.save(D + 'peek_%d.png' % (k // 8 + 1))
