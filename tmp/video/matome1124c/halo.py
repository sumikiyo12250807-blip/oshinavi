# -*- coding: utf-8 -*-
# ピンクの姐さんが白とピンクの背景に埋もれない＝切り抜きの外側に、うすい紫のふち（6px）とやわらかい影を足す（poses/w*・m* を上書き）
import os
import numpy as np
from PIL import Image, ImageFilter
P = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
for f in sorted(os.listdir(P)):
    if not (f.endswith('.png') and f[0] in 'wm' and f[1:-4].isdigit()):
        continue
    im = Image.open(P + f).convert('RGBA')
    pad = 16
    big = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    big.paste(im, (pad, pad), im)
    a = big.getchannel('A')
    ring = a.point(lambda v: 255 if v > 60 else 0).filter(ImageFilter.MaxFilter(13))   # 6px 外へ
    soft = ring.filter(ImageFilter.GaussianBlur(2.5))
    edge = Image.new('RGBA', big.size, (110, 40, 130, 0))
    edge.putalpha(soft.point(lambda v: int(v * 0.75)))
    sh = Image.new('RGBA', big.size, (60, 20, 80, 0))
    sh.putalpha(ring.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.45)))
    out = Image.new('RGBA', big.size, (0, 0, 0, 0))
    out = Image.alpha_composite(out, sh)
    out = Image.alpha_composite(out, edge)
    out = Image.alpha_composite(out, big)
    out.save(P + f)
print('halo ok')
