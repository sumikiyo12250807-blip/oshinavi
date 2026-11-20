# -*- coding: utf-8 -*-
# 2枚目（歩く子）の切り抜きの点検（高さ700）：python look_ny2.py cw1,cw2,cw3 <出力名> → poses/<出力名>.png
import io, re, sys
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
names = sys.argv[1].split(',')
H = 700
boxes = {}
for l in io.open(D + 'cut_ny2.txt', encoding='utf-8'):
    m = re.match(r'(\w+\d) 大きさ .*シート上 \((\d+), (\d+), (\d+), (\d+)\)', l)
    if m:
        boxes[m.group(1)] = tuple(int(m.group(i)) for i in range(2, 6))
sheet = Image.open(D + 'sheet2.png').convert('RGB')
rows = []
for n in names:
    x0, y0, x1, y1 = boxes[n]
    o = sheet.crop((max(0, x0 - 30), max(0, y0 - 30), min(sheet.width, x1 + 30), min(sheet.height, y1 + 30)))
    o = o.resize((int(o.width * H / o.height), H), Image.LANCZOS)
    p = Image.open(D + 'poses/%s.png' % n).convert('RGBA')
    g = Image.new('RGB', (p.width + 60, p.height + 60), (120, 120, 120))
    g.paste(p, (30, 30), p)
    g = g.resize((int(g.width * H / g.height), H), Image.LANCZOS)
    r = Image.new('RGB', (o.width + g.width + 20, H + 40), (20, 20, 20))
    r.paste(o, (0, 40)); r.paste(g, (o.width + 20, 40))
    ImageDraw.Draw(r).text((6, 6), n, fill=(255, 255, 0))
    rows.append(r)
W = sum(r.width + 20 for r in rows)
out = Image.new('RGB', (W, H + 40), (20, 20, 20))
x = 0
for r in rows:
    out.paste(r, (x, 0)); x += r.width + 20
out.save(D + 'poses/%s.png' % sys.argv[2])
