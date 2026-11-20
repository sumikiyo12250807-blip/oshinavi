# -*- coding: utf-8 -*-
# すちこ「こっちの画像の方がいい」＝姐さん（あごに水色の髭の剃り跡・背景透明）のスポーツ9人に差し替え → sheet_n.png・poses を空にする・alpha を数える
import shutil, os
import numpy as np
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
shutil.copyfile('C:/Users/user/Downloads/sports_neesan_1116.png', D + 'sheet_n.png')
P = D + 'poses/'
for f in os.listdir(P):
    if f.endswith('.png'):
        os.remove(P + f)
im = Image.open(D + 'sheet_n.png')
a = np.asarray(im.convert('RGBA'))[:, :, 3]
open(D + 'new_sheet.txt', 'w', encoding='utf-8').write('%s %s alpha 0の割合 %.2f 255の割合 %.2f 中間 %.2f\n' % (im.size, im.mode, (a == 0).mean(), (a == 255).mean(), ((a > 0) & (a < 255)).mean()))
