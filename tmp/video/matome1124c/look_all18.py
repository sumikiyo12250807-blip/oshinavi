# -*- coding: utf-8 -*-
# 切り抜き 18 人（a1〜a9・b1〜b9）を暗い灰色の地に原寸で並べる → look_a.png / look_b.png（頭・羽・尾・髪の先の欠けを見る）
import sys
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
for px in ('a', 'b'):
    ims = [Image.open(D + 'poses/%s%d.png' % (px, k)) for k in range(1, 10)]
    cw, ch = 540, 480
    g = Image.new('RGB', (cw * 3, ch * 3), (60, 60, 70))
    d = ImageDraw.Draw(g)
    for i, im in enumerate(ims):
        x, y = (i % 3) * cw, (i // 3) * ch
        g.paste(im, (x + (cw - im.width) // 2, y + 30), im)
        d.rectangle([x + (cw - im.width) // 2, y + 30, x + (cw - im.width) // 2 + im.width - 1, y + 30 + im.height - 1], outline=(255, 255, 0))
        d.text((x + 8, y + 6), '%s%d' % (px, i + 1), fill=(255, 255, 255))
    g.save(D + 'look_%s.png' % px)
