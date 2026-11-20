# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/frames/'
T = [0.6, 5.0, 9.5, 13.0, 17.0, 19.4, 20.2, 23.0, 28.0, 35.0, 41.0, 47.0, 55.0, 61.0, 70.0, 73.6]
w, h = 270, 480
out = Image.new('RGB', (8 * (w + 6), 2 * (h + 30)), (30, 30, 30))
for i, t in enumerate(T):
    im = Image.open(D + 'h_%05.1f.png' % t).convert('RGB').resize((w, h))
    x, y = (i % 8) * (w + 6), (i // 8) * (h + 30)
    out.paste(im, (x, y + 26))
    ImageDraw.Draw(out).text((x + 4, y + 4), '%.1f' % t, fill=(255, 255, 255))
out.save(D + '../contact16.png')
