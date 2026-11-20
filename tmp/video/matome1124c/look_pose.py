# -*- coding: utf-8 -*-
# 切り抜きの点検（1人ずつ大きく）：元の絵（黒の上）と切り抜き（灰色の上）を同じ大きさで横に並べる・3人ずつ1枚
#   使い方: python inspect.py a1,a2,a3 <出力名>   → poses/<出力名>.png
#   cut9_<シート>.txt のシート上の箱を使い、元の絵は箱より 30px 広く取る（隣のかけら・欠けが分かるように）
import io, re, sys
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
names = sys.argv[1].split(',')
H = 700
boxes = {}
for sh in 'k':
    try:
        for l in io.open(D + 'cut9_%s.txt' % sh, encoding='utf-8'):
            m = re.match(r'(\w\d) 大きさ .*シート上 \((\d+), (\d+), (\d+), (\d+)\)', l)
            if m:
                boxes[m.group(1)] = tuple(int(m.group(i)) for i in range(2, 6))
    except FileNotFoundError:
        pass
rows = []
for n in names:
    sheet = Image.open(D + 'sheet_%s.png' % n[0]).convert('RGBA')
    flat = Image.alpha_composite(Image.new('RGBA', sheet.size, (0, 0, 0, 255)), sheet).convert('RGB')
    x0, y0, x1, y1 = boxes[n]
    o = flat.crop((max(0, x0 - 30), max(0, y0 - 30), min(sheet.width, x1 + 30), min(sheet.height, y1 + 30)))
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
out.save(D + 'poses/%s.png' % sys.argv[2])
