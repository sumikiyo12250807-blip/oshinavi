# -*- coding: utf-8 -*-
# 11/24 クラシックとおでかけ：同じ服で動いた絵 outing_move_1124a〜c を切って v1〜v9 → 元の絵 w1〜w9 と背の高さでそろえる
#   → e（s の動き）・f（t の動き＝反転）→ contact_move.png（元・動いた を組で並べる）
#   頭より上に物を掲げた子は掲げた物のぶん背が高い＝高さの比を少し足す（1 グラスを掲げて乾杯・5 帽子を振る）
import io, os, subprocess, sys
from PIL import Image, ImageOps
sys.stdout.reconfigure(encoding='utf-8')
V = 'C:/Users/user/oshinavi/tmp/video/'
D = V + 'matome1124c/'
DL = 'C:/Users/user/Downloads/'
out = io.open(D + 'move_cut1124.txt', 'w', encoding='utf-8')
ims = [Image.open(DL + 'outing_move_1124%s.png' % k).convert('RGBA') for k in ('a', 'b', 'c')]
for k, i in enumerate(ims, 1):
    out.write('%d %s 隅 %s\n' % (k, i.size, i.getchannel('A').getpixel((5, 5))))
W = max(i.width for i in ims)
ims = [i.resize((W, round(i.height * W / i.width)), Image.LANCZOS) for i in ims]
sh = Image.new('RGBA', (W, sum(i.height for i in ims)), (0, 0, 0, 0))
y = 0
for i in ims:
    sh.alpha_composite(i, (0, y)); y += i.height
sh.save(D + 'sheet_v.png')
r = subprocess.run([sys.executable, V + 'shuyaku1117/cut17.py', 'sheet_v.png', 'v', D], capture_output=True, text=True, encoding='utf-8', errors='replace')
out.write('cut rc %d %s\n' % (r.returncode, r.stderr[-400:]))
if os.path.exists(D + 'cut17_v.txt'):
    out.write(io.open(D + 'cut17_v.txt', encoding='utf-8').read())
UP = {1: 1.04, 5: 1.04}
tiles = []
for k in range(1, 10):
    pw, pv = D + 'poses/w%d.png' % k, D + 'poses/v%d.png' % k
    if not os.path.exists(pv):
        out.write('無い v%d\n' % k); continue
    w, v = Image.open(pw).convert('RGBA'), Image.open(pv).convert('RGBA')
    rr = w.height / v.height * UP.get(k, 1.0)
    v2 = v.resize((round(v.width * rr), round(v.height * rr)), Image.LANCZOS)
    v2.save(D + 'poses/e%d.png' % k)
    ImageOps.mirror(v2).save(D + 'poses/f%d.png' % k)
    out.write('%d w %s → e %s 倍率 %.3f\n' % (k, w.size, v2.size, rr))
    tiles += [w, v2]
th = 360
sc = th / max(t.height for t in tiles)
row = Image.new('RGBA', (sum(int(t.width * sc) + 20 for t in tiles) + 20, th + 40), (40, 40, 70, 255))
x = 20
for t in tiles:
    t2 = t.resize((int(t.width * sc), int(t.height * sc)), Image.LANCZOS)
    row.alpha_composite(t2, (x, 20 + th - t2.height)); x += t2.width + 20
row.convert('RGB').save(D + 'contact_move.png')
out.close()
