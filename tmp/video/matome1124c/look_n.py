# -*- coding: utf-8 -*-
# 新しい姐さん9人：元の絵（シートの同じ所・黒地）と切り抜き（緑の地）を高さ 700 で横に並べる → look_n1〜9.png
import io, re
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = Image.open(D + 'sheet_n.png').convert('RGBA')
blk = Image.alpha_composite(Image.new('RGBA', src.size, (0, 0, 0, 255)), src).convert('RGB')
boxes = {}
for l in io.open(D + 'cut9_w.txt', encoding='utf-8'):
    m = re.match(r'w(\d) 大きさ .* シート上 \((\d+), (\d+), (\d+), (\d+)\)', l)
    if m:
        boxes[int(m.group(1))] = tuple(int(m.group(i)) for i in range(2, 6))
th = 700
for k, (x0, y0, x1, y1) in boxes.items():
    pad = 30
    b = (max(0, x0 - pad), max(0, y0 - pad), min(src.width, x1 + pad), min(src.height, y1 + pad))
    o = blk.crop(b)
    sc = th / o.height
    o = o.resize((int(o.width * sc), th), Image.LANCZOS)
    cut = Image.open(D + 'poses/w%d.png' % k).convert('RGBA')
    g = Image.new('RGB', o.size, (0, 150, 60))
    c2 = cut.resize((int(cut.width * sc), int(cut.height * sc)), Image.LANCZOS)
    g.paste(c2, (int((x0 - b[0]) * sc), int((y0 - b[1]) * sc)), c2)
    row = Image.new('RGB', (o.width * 2 + 20, th), (40, 40, 40))
    row.paste(o, (0, 0)); row.paste(g, (o.width + 20, 0))
    ImageDraw.Draw(row).text((6, 6), 'w%d' % k, fill=(255, 255, 255))
    row.save(D + 'look_n%d.png' % k)
print('ok')
