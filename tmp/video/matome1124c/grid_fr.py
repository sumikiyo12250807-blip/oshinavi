# -*- coding: utf-8 -*-
# frames/h_*.png を秒の順に横並び（1枚 360×640）→ frames/grid.png
import glob, sys
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/frames/'
ts = sys.argv[1].split(',')
ims = []
for t in ts:
    im = Image.open(D + 'h_%05.1f.png' % float(t)).convert('RGB').resize((360, 640), Image.LANCZOS)
    ImageDraw.Draw(im).text((6, 6), t, fill=(255, 255, 0))
    ims.append(im)
n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
rows = (len(ims) + n - 1) // n
g = Image.new('RGB', (n * 365, rows * 645), (0, 0, 0))
for i, im in enumerate(ims):
    g.paste(im, ((i % n) * 365, (i // n) * 645))
g.save(D + 'grid.png')
