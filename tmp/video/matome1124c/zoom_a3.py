# -*- coding: utf-8 -*-
# a3 の下のブーツのあたり（シート x 820〜1120・y 330〜500）を黒の上で4倍に拡大・20px ごとの目盛り
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = Image.open(D + 'sheet_a.png').convert('RGBA')
flat = Image.alpha_composite(Image.new('RGBA', src.size, (0, 0, 0, 255)), src).convert('RGB')
x0, y0, x1, y1 = 820, 330, 1120, 500
c = flat.crop((x0, y0, x1, y1)).resize(((x1 - x0) * 4, (y1 - y0) * 4), Image.LANCZOS)
d = ImageDraw.Draw(c)
for x in range(x0, x1, 20):
    d.line([((x - x0) * 4, 0), ((x - x0) * 4, 12)], fill=(0, 255, 0)); d.text(((x - x0) * 4 + 2, 14), str(x), fill=(0, 255, 0))
for y in range(y0, y1, 20):
    d.line([(0, (y - y0) * 4), (12, (y - y0) * 4)], fill=(0, 255, 0)); d.text((14, (y - y0) * 4 + 2), str(y), fill=(0, 255, 0))
c.save(D + 'poses/zoom_a3.png')
