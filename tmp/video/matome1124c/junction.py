# -*- coding: utf-8 -*-
# 上の人の足（すそ）と下の人の頭のつなぎ目（6か所）を拡大して、10px ごとの目盛りを付けて並べる（このシート用の範囲）
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
sh = Image.open(D + 'sheet.png').convert('RGB')
AREAS = [(60, 390, 420, 480), (440, 420, 830, 490), (870, 420, 1220, 490),
         (0, 820, 460, 930), (380, 800, 870, 900), (830, 860, 1254, 950)]
tiles = []
for (x0, a, x1, b) in AREAS:
    t = sh.crop((x0, a, x1, b)).resize(((x1 - x0) * 2, (b - a) * 2))
    d = ImageDraw.Draw(t)
    for y in range(a - a % 10, b, 10):
        if y < a:
            continue
        yy = (y - a) * 2
        d.line((0, yy, 14 if y % 50 else 40, yy), fill=(0, 200, 0))
        if y % 50 == 0:
            d.text((44, yy - 6), str(y), fill=(0, 150, 0))
    for x in range(x0 - x0 % 50 + 50, x1, 50):
        d.line(((x - x0) * 2, 0, (x - x0) * 2, 20), fill=(255, 0, 0))
        d.text(((x - x0) * 2 + 3, 2), str(x), fill=(255, 0, 0))
    tiles.append(t)
tw = max(t.width for t in tiles)
out = Image.new('RGB', (2 * tw + 10, sum(max(tiles[i].height, tiles[i + 1].height) + 10 for i in (0, 2, 4))), (40, 40, 40))
y = 0
for i in (0, 2, 4):
    out.paste(tiles[i], (0, y)); out.paste(tiles[i + 1], (tw + 10, y))
    y += max(tiles[i].height, tiles[i + 1].height) + 10
out.save(D + 'poses/junction.png')
