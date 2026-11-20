# -*- coding: utf-8 -*-
# 切り抜きの名前を walk_char の決まりに合わせる（w/m＝1枚目の右向き/反転・a/b＝2枚目の右向き/反転・s/t＝座る子の右向き/反転）
#   1枚目（華やかな九人）a1〜a9 → w1〜w9（人魚 a6 だけ座る子 s6）／2枚目（grid collage）b1〜b9 → a1〜a9
#   先に一時の名前へ写してから置き換える（a と b が入れ替わるので）
import io, os, shutil
from PIL import Image, ImageOps
P = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
tmp = {}
for k in range(1, 10):
    tmp['A%d' % k] = Image.open(P + 'a%d.png' % k).copy()
    tmp['B%d' % k] = Image.open(P + 'b%d.png' % k).copy()
for f in os.listdir(P):
    if f.endswith('.png'):
        os.remove(P + f)
out = []
for k in range(1, 10):
    r, l = ('s', 't') if k == 6 else ('w', 'm')
    im = tmp['A%d' % k]
    im.save(P + '%s%d.png' % (r, k)); ImageOps.mirror(im).save(P + '%s%d.png' % (l, k))
    im2 = tmp['B%d' % k]
    im2.save(P + 'a%d.png' % k); ImageOps.mirror(im2).save(P + 'b%d.png' % k)
    out.append('%s%d/%s%d ← 1枚目 %d  ・  a%d/b%d ← 2枚目 %d' % (r, k, l, k, k, k, k, k))
io.open(P + '../name_poses14.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
