# -*- coding: utf-8 -*-
# 左右反転の子（n1〜n9）を作る＝締めに下りてくる子の向きをそろえる・同じ服が並ぶ時に向きで変化をつける
from PIL import Image, ImageOps
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
for k in range(1, 10):
    ImageOps.mirror(Image.open(D + 'r%d.png' % k)).save(D + 'n%d.png' % k)
