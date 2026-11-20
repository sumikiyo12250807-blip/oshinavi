# -*- coding: utf-8 -*-
# 切り抜きの点検（look_pose の形）：元のシート（白地）と切り抜き（灰色の上）を高さ 700 で横に並べる・3人ずつ → poses/look_a/b/c.png
import io, re
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
H = 700
boxes = {}
for l in io.open(D + 'cut1110.txt', encoding='utf-8'):
    m = re.match(r'(r\d) 大きさ .*シート上 \((\d+), (\d+), (\d+), (\d+)\)', l)
    if m:
        boxes[m.group(1)] = tuple(int(m.group(i)) for i in range(2, 6))
sheet = Image.open(D + 'sheet.png').convert('RGB')
for tag, names in (('a', 'r1 r2 r3'), ('b', 'r4 r5 r6'), ('c', 'r7 r8 r9')):
    rows = []
    for n in names.split():
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
    W = max(r.width for r in rows)
    out = Image.new('RGB', (W, sum(r.height + 10 for r in rows)), (20, 20, 20))
    y = 0
    for r in rows:
        out.paste(r, (0, y)); y += r.height + 10
    out.save(D + 'poses/look_%s.png' % tag)
