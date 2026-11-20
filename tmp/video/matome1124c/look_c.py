# -*- coding: utf-8 -*-
# 切り抜きの点検（1人ずつ大きく・灰色と濃紺の上）：python look_c.py c 1,2,3 名前 → art/<名前>.png
import sys
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
H = 640
rows = []
PX = sys.argv[1]
for k in sys.argv[2].split(','):
    p = Image.open(D + 'poses/%s%s.png' % (PX, k)).convert('RGBA')
    cells = []
    for bg in ((120, 120, 120), (20, 15, 50)):
        g = Image.new('RGB', (p.width + 40, p.height + 40), bg)
        g.paste(p, (20, 20), p)
        cells.append(g.resize((int(g.width * H / g.height), H), Image.LANCZOS))
    r = Image.new('RGB', (sum(c.width for c in cells) + 20, H + 30), (0, 0, 0))
    x = 0
    for c in cells:
        r.paste(c, (x, 30)); x += c.width + 20
    ImageDraw.Draw(r).text((6, 6), PX + k, fill=(255, 255, 0))
    rows.append(r)
W = sum(r.width + 10 for r in rows)
out = Image.new('RGB', (W, max(r.height for r in rows)), (0, 0, 0))
x = 0
for r in rows:
    out.paste(r, (x, 0)); x += r.width + 10
out.save(D + 'art/%s.png' % sys.argv[3])
