# -*- coding: utf-8 -*-
# 1枚目（1536×1024）の3人だけ、ほかの2枚（2172×724）より約1.4倍大きく切れた＝背の高さを2枚目・3枚目の平均にそろえる
#   w/m（元の絵）・v/e/f（動いた絵）・s/t（動画で使う名前）を 1〜3 だけ同じ倍率で縮める
import io
from PIL import Image, ImageOps
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
H = sum(Image.open(D + 'w%d.png' % k).height for k in range(4, 10)) / 6
out = io.open('C:/Users/user/oshinavi/tmp/video/matome1124c/size_fix1124.txt', 'w', encoding='utf-8')
for k in (1, 2, 3):
    w = Image.open(D + 'w%d.png' % k).convert('RGBA')
    r = H / w.height
    for p in ('w', 'v', 'e'):
        im = Image.open(D + '%s%d.png' % (p, k)).convert('RGBA')
        im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
        im.save(D + '%s%d.png' % (p, k))
    w = Image.open(D + 'w%d.png' % k)
    w.save(D + 's%d.png' % k)
    ImageOps.mirror(w).save(D + 'm%d.png' % k)
    ImageOps.mirror(w).save(D + 't%d.png' % k)
    ImageOps.mirror(Image.open(D + 'e%d.png' % k)).save(D + 'f%d.png' % k)
    out.write('%d 倍率 %.3f → w %s e %s\n' % (k, r, w.size, Image.open(D + 'e%d.png' % k).size))
tiles = []
for k in range(1, 10):
    tiles += [Image.open(D + 'w%d.png' % k).convert('RGBA'), Image.open(D + 'e%d.png' % k).convert('RGBA')]
th = 360
sc = th / max(t.height for t in tiles)
row = Image.new('RGBA', (sum(int(t.width * sc) + 20 for t in tiles) + 20, th + 40), (40, 40, 70, 255))
x = 20
for t in tiles:
    t2 = t.resize((int(t.width * sc), int(t.height * sc)), Image.LANCZOS)
    row.alpha_composite(t2, (x, 20 + th - t2.height)); x += t2.width + 20
row.convert('RGB').save('C:/Users/user/oshinavi/tmp/video/matome1124c/contact_move.png')
