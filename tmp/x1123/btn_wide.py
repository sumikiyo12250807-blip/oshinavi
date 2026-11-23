# -*- coding: utf-8 -*-
# すちこがくれた横長の宿ボタン（会場近くのホテルを探す →）を img/btn_hotel_wide.png に＝まわりの余白を切って、軽くする
import io
from PIL import Image
src = 'C:/Users/user/.claude/uploads/6d0ac969-eb80-4bf7-86e5-551288d024a5/5d0a27b2-image.png'
im = Image.open(src)
o = io.open('C:/Users/user/oshinavi/tmp/x1123/btn_wide.txt', 'w', encoding='utf-8')
o.write('元 %s %s\n' % (im.size, im.mode))
im = im.convert('RGBA')
a = im.getchannel('A')
o.write('透明の点あり=%s\n' % (a.getextrema()[0] < 10))
bb = a.point(lambda v: 255 if v > 40 else 0).getbbox()
o.write('中身の箱 %s\n' % (bb,))
im = im.crop((max(bb[0] - 6, 0), max(bb[1] - 6, 0), min(bb[2] + 6, im.width), min(bb[3] + 6, im.height)))
w = 1000
im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
im.save('C:/Users/user/oshinavi/img/btn_hotel_wide.png', optimize=True)
import os
o.write('できた %s %dKB\n' % (im.size, os.path.getsize('C:/Users/user/oshinavi/img/btn_hotel_wide.png') // 1024))
