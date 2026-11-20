# -*- coding: utf-8 -*-
# つなぎ目の拡大：sheet_b の b5/b8（x520〜770 y740〜900）・b2/b5（x514〜765 y340〜470）・b6/b9・b4/b7、sheet_a の a6/a9（灰色の地に置いて3倍）
import sys
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
R = [('b', (520, 740, 770, 900)), ('b', (514, 340, 765, 470)), ('b', (900, 760, 1150, 900)), ('b', (100, 760, 390, 900)), ('a', (960, 740, 1305, 880))]
tiles = []
for tag, box in R:
    s = Image.open(D + 'sheet_%s.png' % tag).convert('RGBA').crop(box)
    g = Image.new('RGBA', s.size, (60, 160, 60, 255))
    g.alpha_composite(s)
    tiles.append(g.convert('RGB').resize((s.width * 2, s.height * 2), Image.NEAREST))
W = max(t.width for t in tiles)
out = Image.new('RGB', (W * 2 + 10, sum(t.height + 10 for t in tiles[::2])), (0, 0, 0))
y = 0
for i in range(0, len(tiles), 2):
    out.paste(tiles[i], (0, y))
    if i + 1 < len(tiles):
        out.paste(tiles[i + 1], (W + 10, y))
    y += max(t.height for t in tiles[i:i + 2]) + 10
out.save(D + 'poses/junction.png')
