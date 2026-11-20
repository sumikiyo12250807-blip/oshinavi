# -*- coding: utf-8 -*-
# python peek_top.py c6 x0 y0 x1 y1 → art/peek.png（切り抜きの一部を 6 倍・濃紺の地・10 画素ごとの目盛り）
import sys
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
p = Image.open(D + 'poses/%s.png' % sys.argv[1]).convert('RGBA')
x0, y0, x1, y1 = [int(v) for v in sys.argv[2:6]]
c = p.crop((x0, y0, x1, y1))
g = Image.new('RGBA', c.size, (20, 15, 50, 255)); g.alpha_composite(c)
S = 6
g = g.resize((c.width * S, c.height * S), Image.NEAREST).convert('RGB')
d = ImageDraw.Draw(g)
for x in range(0, c.width, 10):
    d.line([(x * S, 0), (x * S, 8)], fill=(255, 255, 0)); d.text((x * S + 2, 10), str(x0 + x), fill=(255, 255, 0))
for y in range(0, c.height, 10):
    d.line([(0, y * S), (8, y * S)], fill=(0, 255, 0)); d.text((10, y * S + 2), str(y0 + y), fill=(0, 255, 0))
g.save(D + 'art/peek.png')
