# -*- coding: utf-8 -*-
"""r1c1（3体が1カットに繋がった帯）を3体に割る。左＝正面・指を立てるポーズを採用。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image

im = Image.open("tmp/char6/r1c1.png").convert("RGBA")
for name, (x0, x1) in {"front1": (0, 278), "front2": (281, 506), "side1": (519, 699)}.items():
    cut = im.crop((x0, 0, x1, im.size[1]))
    b = cut.getbbox()
    if b:
        cut = cut.crop(b)
    p = "tmp/char6/%s.png" % name
    cut.save(p)
    print("%s  %dx%d" % (p, cut.size[0], cut.size[1]))
