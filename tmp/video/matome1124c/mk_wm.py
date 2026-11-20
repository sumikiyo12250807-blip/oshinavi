# -*- coding: utf-8 -*-
# 11/15 グルメの子：1枚目（目を開けた・細かい絵）g1〜g9 → w1〜w9（シートの向き＝右向き）／m1〜m9（左右反転＝左向き）
#   2枚目（目を閉じた・筆の絵）c1〜c9 → a1〜a9（右向き）／b1〜b9（反転＝左向き）・全員歩く子
#   g：1 ケーキ／2 すし／3 ピザ／4 ラーメン／5 スイーツの皿／6 コーヒー／7 BBQ（グリル）／8 アイス（ひまわり帽）／9 海の幸（カニ）
#   c：1 ケーキ／2 すし／3 パスタ／4 パン／5 点心（せいろ）／6 コーヒー／7 ビール（使わない）／8 たこ焼き／9 BBQ（グリル）
import os, re
from PIL import Image, ImageOps
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
for f in os.listdir(D):
    if re.fullmatch(r'[wmstab]\d\.png', f):
        os.remove(D + f)
for k in range(1, 10):
    for src, r, l in (('g', 'w', 'm'), ('c', 'a', 'b')):
        im = Image.open(D + '%s%d.png' % (src, k))
        im.save(D + '%s%d.png' % (r, k))
        ImageOps.mirror(im).save(D + '%s%d.png' % (l, k))
print('ok')
