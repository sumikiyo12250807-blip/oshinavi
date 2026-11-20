# -*- coding: utf-8 -*-
# 切り抜きの点検（1人ずつ大きく・灰色と濃紺の上）：python look_p.py 1,2,3 名前 → poses/<名前>.png
import sys
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
H = 760
rows = []
for k in sys.argv[1].split(','):
    p = Image.open(D + 'poses/cp%s.png' % k).convert('RGBA')
    cells = []
    for bg in ((120, 120, 120), (20, 15, 50)):
        g = Image.new('RGB', (p.width + 40, p.height + 40), bg)
        g.paste(p, (20, 20), p)
        cells.append(g.resize((int(g.width * H / g.height), H), Image.LANCZOS))
    r = Image.new('RGB', (sum(c.width for c in cells) + 20, H + 30), (0, 0, 0))
    x = 0
    for c in cells:
        r.paste(c, (x, 30)); x += c.width + 20
    ImageDraw.Draw(r).text((6, 6), 'cp' + k, fill=(255, 255, 0))
    rows.append(r)
W = max(r.width for r in rows)
out = Image.new('RGB', (W, sum(r.height + 10 for r in rows)), (0, 0, 0))
y = 0
for r in rows:
    out.paste(r, (0, y)); y += r.height + 10
out.save(D + 'poses/%s.png' % sys.argv[2])
