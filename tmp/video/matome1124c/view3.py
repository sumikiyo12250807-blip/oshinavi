# -*- coding: utf-8 -*-
# 切り抜きを暗い地に大きく並べて、破片が残っていないか見る（引数＝番号）
import sys
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
ks = sys.argv[1].split(',')
ims = [Image.open(D + 'p%s.png' % k) for k in ks]
th = 700
ims = [im.resize((int(im.width * th / im.height), th), Image.LANCZOS) for im in ims]
out = Image.new('RGB', (sum(i.width + 20 for i in ims), th + 20), (40, 30, 70))
x = 10
for im in ims:
    out.paste(im, (x, 10), im); x += im.width + 20
out.save(D + 'view.png')
