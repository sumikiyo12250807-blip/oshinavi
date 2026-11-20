# -*- coding: utf-8 -*-
# r3 の靴と r6 のベレーのつなぎ目を拡大（シート x 1040〜1320・y 320〜390 を 5 倍）＋切り抜き r6 の頭 → zoom6.png
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
s = Image.open(D + 'sheet.png').convert('RGB').crop((1040, 320, 1320, 390)).resize((1400, 350), Image.NEAREST)
d = ImageDraw.Draw(s)
for y in range(320, 391, 10):
    d.line([(0, (y - 320) * 5), (1400, (y - 320) * 5)], fill=(0, 200, 0))
    d.text((2, (y - 320) * 5 + 2), str(y), fill=(0, 150, 0))
p = Image.open(D + 'poses/r6.png').convert('RGBA')
top = p.crop((0, 0, p.width, 120))
g = Image.new('RGB', (top.width, top.height), (120, 120, 120))
g.paste(top, (0, 0), top)
g = g.resize((g.width * 2, g.height * 2))
out = Image.new('RGB', (max(1400, g.width), 350 + g.height + 10), (20, 20, 20))
out.paste(s, (0, 0)); out.paste(g, (0, 360))
out.save(D + 'zoom6.png')
