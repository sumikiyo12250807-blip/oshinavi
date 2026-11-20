# -*- coding: utf-8 -*-
# Downloads に保存した姐さん3枚：大きさ・透明かどうか・縮めて縦に並べた見本
from PIL import Image
import io
D = 'C:/Users/user/Downloads/'
out = io.open('C:/Users/user/oshinavi/tmp/video/matome1124c/look_dl.txt', 'w', encoding='utf-8')
ims = []
for n in ('outing_chibi_1124a.png', 'outing_chibi_1124b.png', 'outing_chibi_1124c.png'):
    im = Image.open(D + n)
    a = im.getchannel('A') if im.mode == 'RGBA' else None
    clear = sum(1 for v in a.getdata() if v < 10) / (im.width * im.height) if a else 0
    out.write('%s %s %s 透明の割合 %.2f\n' % (n, im.size, im.mode, clear))
    t = im.convert('RGBA'); t.thumbnail((600, 300))
    ims.append(t)
W = max(t.width for t in ims); H = sum(t.height for t in ims)
s = Image.new('RGBA', (W, H), (60, 60, 60, 255)); y = 0
for t in ims:
    s.alpha_composite(t, (0, y)); y += t.height
s.save('C:/Users/user/oshinavi/tmp/video/matome1124c/look_dl.png')
