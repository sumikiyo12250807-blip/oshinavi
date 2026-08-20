# -*- coding: utf-8 -*-
"""シートの背景が透過か白かを確かめる。"""
import io, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image

im = Image.open(sys.argv[1]).convert("RGBA")
W, H = im.size
px = im.load()
c = collections.Counter()
for y in range(0, H, 7):
    for x in range(0, W, 7):
        r, g, b, a = px[x, y]
        if a < 8:
            c["透明"] += 1
        elif r > 245 and g > 245 and b > 245:
            c["ほぼ白"] += 1
        else:
            c["絵"] += 1
print(im.size, dict(c))
print("四隅:", px[0, 0], px[W - 1, 0], px[0, H - 1], px[W - 1, H - 1])
print("中央上の帯 y=500 のサンプル:", [px[x, 500] for x in range(0, W, 200)])
