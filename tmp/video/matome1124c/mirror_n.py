# -*- coding: utf-8 -*-
# 新しい姐さん9人の反転（m1〜m9）を作る
from PIL import Image, ImageOps
P = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
for k in range(1, 10):
    ImageOps.mirror(Image.open(P + 'w%d.png' % k)).save(P + 'm%d.png' % k)
print('ok')
