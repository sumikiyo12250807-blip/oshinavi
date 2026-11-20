# -*- coding: utf-8 -*-
# 切り抜いた9人（元の向き k）を灰色の地に等倍で並べる＝頭のてっぺん・足先・衣装の欠けを見る
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
for pre in 'kn':
    ims = [Image.open(D + '%s%d.png' % (pre, i)).convert('RGBA') for i in range(1, 10)]
    cw, ch = max(i.width for i in ims) + 20, max(i.height for i in ims) + 20
    L = Image.new('RGB', (cw * 3, ch * 3), (120, 120, 120))
    for j, im in enumerate(ims):
        L.paste(im, ((j % 3) * cw + 10, (j // 3) * ch + 10), im)
    L.save(D + 'look_all_%s.png' % pre)
