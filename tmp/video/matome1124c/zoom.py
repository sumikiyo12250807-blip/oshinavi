# -*- coding: utf-8 -*-
# 気になる3か所を4倍に拡大（5px ごとの目盛り）
import sys
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
sh = Image.open(D + 'sheet.png').convert('RGB')
AREAS = [(170, 840, 300, 935), (590, 835, 700, 905), (840, 875, 1000, 925)]
tiles = []
for (x0, y0, x1, y1) in AREAS:
    t = sh.crop((x0, y0, x1, y1)).resize(((x1 - x0) * 4, (y1 - y0) * 4), Image.NEAREST)
    d = ImageDraw.Draw(t)
    for y in range(y0, y1, 5):
        d.line((0, (y - y0) * 4, 12 if y % 10 else 30, (y - y0) * 4), fill=(0, 160, 0))
        if y % 10 == 0:
            d.text((32, (y - y0) * 4 - 5), str(y), fill=(0, 120, 0))
    for x in range(x0, x1, 5):
        d.line(((x - x0) * 4, 0, (x - x0) * 4, 12 if x % 10 else 30), fill=(255, 0, 0))
        if x % 10 == 0:
            d.text(((x - x0) * 4 + 2, 14), str(x), fill=(255, 0, 0))
    tiles.append(t)
out = Image.new('RGB', (max(t.width for t in tiles), sum(t.height + 10 for t in tiles)), (40, 40, 40))
y = 0
for t in tiles:
    out.paste(t, (0, y)); y += t.height + 10
out.save(D + 'poses/zoom.png')
