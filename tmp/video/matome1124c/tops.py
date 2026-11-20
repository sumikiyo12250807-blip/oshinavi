# -*- coding: utf-8 -*-
# 下の段の切り抜き（p4〜p9）の頭の上 260px を緑の地に並べる（上の段の靴のかけらが残っていないか）
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
a = [Image.open(D + 'p%d.png' % k) for k in (4, 5, 6, 7, 8, 9)]
o = Image.new('RGB', (sum(i.width for i in a) + 60, 260), (0, 150, 60))
x = 0
for i in a:
    c = i.crop((0, 0, i.width, 260))
    o.paste(c, (x, 0), c)
    x += i.width + 10
o.save(D + 'tops.png')
