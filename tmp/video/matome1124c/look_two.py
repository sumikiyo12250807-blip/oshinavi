# -*- coding: utf-8 -*-
# a4・b5 を原寸の 1.6 倍で並べる（足の下の線が消えたか・足が欠けていないか）→ look_two.png
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
ims = [Image.open(D + 'poses/%s.png' % n) for n in ('a4', 'b5')]
ims = [im.resize((int(im.width * 1.6), int(im.height * 1.6))) for im in ims]
g = Image.new('RGB', (sum(i.width for i in ims) + 60, max(i.height for i in ims) + 40), (60, 60, 70))
x = 20
for im in ims:
    g.paste(im, (x, 20), im)
    x += im.width + 20
g.save(D + 'look_two.png')
