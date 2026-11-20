# -*- coding: utf-8 -*-
# 元シート（濃紺の地）と切り抜き（同じ位置に置き直し）を左右に並べて拡大：python zoom_c.py k → art/zoom_k.png
import sys
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
k = int(sys.argv[1])
pos = {}
for line in open(D + 'cut9_c.txt', encoding='utf-8'):
    if line.startswith('c') and 'シート上' in line:
        nm = line.split()[0]
        nums = line.split('シート上')[1].strip(' ()\n').split(',')
        pos[nm] = [int(x) for x in nums]
x0, y0, x1, y1 = pos['c%d' % k]
X0, Y0, X1, Y1 = max(0, x0 - 40), max(0, y0 - 40), min(1536, x1 + 40), min(1024, y1 + 40)
sheet = Image.open(D + 'sheet.png').convert('RGBA')
L = Image.new('RGBA', sheet.size, (20, 15, 50, 255)); L.alpha_composite(sheet)
R = Image.new('RGBA', sheet.size, (20, 15, 50, 255)); R.alpha_composite(Image.open(D + 'poses/c%d.png' % k).convert('RGBA'), (x0, y0))
a, b = L.crop((X0, Y0, X1, Y1)), R.crop((X0, Y0, X1, Y1))
s = 2
o = Image.new('RGB', (a.width * 2 * s + 20, a.height * s), (255, 255, 0))
o.paste(a.resize((a.width * s, a.height * s)).convert('RGB'), (0, 0))
o.paste(b.resize((a.width * s, a.height * s)).convert('RGB'), (a.width * s + 20, 0))
o.save(D + 'art/zoom_%d.png' % k)
