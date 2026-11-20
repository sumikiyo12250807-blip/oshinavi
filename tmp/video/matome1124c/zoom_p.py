# -*- coding: utf-8 -*-
# 切り抜きを濃い緑の地で拡大して欠け・残りかすを見る
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
out = Image.new('RGB', (1800, 1500), (0, 110, 50))
x = y = 0
for k in range(1, 10):
    im = Image.open(D + 'p%d.png' % k)
    r = min(590 / im.width, 490 / im.height)
    a = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    out.paste(a, ((k - 1) % 3 * 600 + 5, (k - 1) // 3 * 500 + 5), a)
out.save(D + 'zoom.png')
