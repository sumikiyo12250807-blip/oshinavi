# -*- coding: utf-8 -*-
# 切り抜きの点検（1人ずつ大きく）：元の絵（箱より30広く）と切り抜き（暗い紺の上）を高さ700で横に並べる → poses/look_<名前>.png
import io, re, sys
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
names = sys.argv[1].split(',')
H = 700
boxes = {}
for l in io.open(D + 'cut_rain.txt', encoding='utf-8'):
    m = re.match(r'(r\d) 大きさ .*シート上 \((\d+), (\d+), (\d+), (\d+)\)', l)
    if m:
        boxes[m.group(1)] = tuple(int(m.group(i)) for i in range(2, 6))
sheet = Image.open(D + 'sheet.png').convert('RGB')
rows = []
for n in names:
    x0, y0, x1, y1 = boxes[n]
    o = sheet.crop((max(0, x0 - 30), max(0, y0 - 30), min(sheet.width, x1 + 30), min(sheet.height, y1 + 30)))
    o = o.resize((int(o.width * H / o.height), H), Image.LANCZOS)
    p = Image.open(D + 'poses/%s.png' % n).convert('RGBA')
    g = Image.new('RGB', (p.width + 60, p.height + 60), (25, 20, 60))
    g.paste(p, (30, 30), p)
    g = g.resize((int(g.width * H / g.height), H), Image.LANCZOS)
    r = Image.new('RGB', (o.width + g.width + 20, H + 40), (20, 20, 20))
    r.paste(o, (0, 40)); r.paste(g, (o.width + 20, 40))
    ImageDraw.Draw(r).text((6, 6), n, fill=(255, 255, 0))
    rows.append(r)
W = sum(r.width + 10 for r in rows)
out = Image.new('RGB', (W, H + 40), (20, 20, 20))
x = 0
for r in rows:
    out.paste(r, (x, 0)); x += r.width + 10
out.save(D + 'poses/look_%s.png' % '_'.join(names))
