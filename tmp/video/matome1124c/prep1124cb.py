# -*- coding: utf-8 -*-
# 11/24 クラシックとおでかけ：よそ行きの姐さん 3枚（3人横1列）を縦に積んで sheet.png → cut17 で w1〜w9・反転 m1〜m9 → contact_cut.png
import io, os, subprocess, sys
from PIL import Image, ImageOps
V = 'C:/Users/user/oshinavi/tmp/video/'
D = V + 'matome1124c/'
DL = 'C:/Users/user/Downloads/'
o = io.open(D + 'prep1124cb.txt', 'w', encoding='utf-8')
ims = [Image.open(DL + 'outing_chibi_1124%s.png' % k) for k in ('a', 'b', 'c')]
for k, im in enumerate(ims, 1):
    o.write('%d %s %s 隅 %s\n' % (k, im.mode, im.size, im.getchannel('A').getpixel((5, 5)) if im.mode == 'RGBA' else '-'))
W = max(i.width for i in ims)
ims = [i.convert('RGBA').resize((W, round(i.height * W / i.width)), Image.LANCZOS) for i in ims]
sh = Image.new('RGBA', (W, sum(i.height for i in ims)), (0, 0, 0, 0))
y = 0
for im in ims:
    sh.alpha_composite(im, (0, y)); y += im.height
sh.save(D + 'sheet.png')
for f in os.listdir(D + 'poses'):
    os.remove(D + 'poses/' + f)
r = subprocess.run([sys.executable, V + 'shuyaku1117/cut17.py', 'sheet.png', 'w', D], capture_output=True, text=True, encoding='utf-8', errors='replace')
o.write('cut rc %d %s\n' % (r.returncode, r.stderr[-800:]))
if os.path.exists(D + 'cut17_w.txt'):
    o.write(io.open(D + 'cut17_w.txt', encoding='utf-8').read())
for k in range(1, 10):
    p = D + 'poses/w%d.png' % k
    if os.path.exists(p):
        ImageOps.mirror(Image.open(p)).save(D + 'poses/m%d.png' % k)
tiles = [Image.open(D + 'poses/w%d.png' % k).convert('RGBA') for k in range(1, 10) if os.path.exists(D + 'poses/w%d.png' % k)]
th = 360
row = Image.new('RGBA', (sum(int(t.width * th / t.height) + 20 for t in tiles) + 20, th + 40), (40, 40, 70, 255))
x = 20
for t in tiles:
    t2 = t.resize((int(t.width * th / t.height), th), Image.LANCZOS)
    row.alpha_composite(t2, (x, 20)); x += t2.width + 20
row.convert('RGB').save(D + 'contact_cut.png')
o.close()
