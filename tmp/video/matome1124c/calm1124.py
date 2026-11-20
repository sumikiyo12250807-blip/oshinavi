# -*- coding: utf-8 -*-
# 11/20 すちこ「普段着でおとなしい感じのファッションが最初の曲に合う　背景も夕暮れ時でしょ　清楚な感じよ」
#   ①今のよそ行きの切り抜き（poses）を poses_outing に控える（2本目のライブで使う）
#   ②普段着 calm_chibi_1124a〜c → w1〜w9／m1〜m9、動いた絵 calm_move_1124a〜c → v1〜v9 → 背をそろえて e／f
#   ③1枚ずつ紙の形が違っても、9人の背の高さをそろえる（2枚目・3枚目の平均ではなく9人の中央値に）→ s／t を作り直す → contact
import io, os, shutil, subprocess, sys, statistics
from PIL import Image, ImageOps
V = 'C:/Users/user/oshinavi/tmp/video/'
D = V + 'matome1124c/'
P = D + 'poses/'
DL = 'C:/Users/user/Downloads/'
o = io.open(D + 'calm1124.txt', 'w', encoding='utf-8')
if not os.path.exists(D + 'poses_outing'):
    shutil.copytree(P, D + 'poses_outing')
o.write('控え poses_outing %d 枚\n' % len(os.listdir(D + 'poses_outing')))
for f in os.listdir(P):
    os.remove(P + f)


def sheet(names, out):
    ims = [Image.open(DL + n).convert('RGBA') for n in names]
    for n, im in zip(names, ims):
        o.write('%s %s 隅 %s\n' % (n, im.size, im.getchannel('A').getpixel((5, 5))))
    W = max(i.width for i in ims)
    ims = [i.resize((W, round(i.height * W / i.width)), Image.LANCZOS) for i in ims]
    sh = Image.new('RGBA', (W, sum(i.height for i in ims)), (0, 0, 0, 0))
    y = 0
    for im in ims:
        sh.alpha_composite(im, (0, y)); y += im.height
    sh.save(D + out)


sheet(['calm_chibi_1124%s.png' % k for k in 'abc'], 'sheet.png')
r = subprocess.run([sys.executable, V + 'shuyaku1117/cut17.py', 'sheet.png', 'w', D], capture_output=True, text=True, encoding='utf-8', errors='replace')
o.write('cut w rc %d %s\n' % (r.returncode, r.stderr[-300:]))
o.write(io.open(D + 'cut17_w.txt', encoding='utf-8').read() if os.path.exists(D + 'cut17_w.txt') else '')
sheet(['calm_move_1124%s.png' % k for k in 'abc'], 'sheet_v.png')
r = subprocess.run([sys.executable, V + 'shuyaku1117/cut17.py', 'sheet_v.png', 'v', D], capture_output=True, text=True, encoding='utf-8', errors='replace')
o.write('cut v rc %d %s\n' % (r.returncode, r.stderr[-300:]))
o.write(io.open(D + 'cut17_v.txt', encoding='utf-8').read() if os.path.exists(D + 'cut17_v.txt') else '')
H = statistics.median(Image.open(P + 'w%d.png' % k).height for k in range(1, 10))
tiles = []
for k in range(1, 10):
    w = Image.open(P + 'w%d.png' % k).convert('RGBA')
    rw = H / w.height
    w = w.resize((round(w.width * rw), round(w.height * rw)), Image.LANCZOS)
    w.save(P + 'w%d.png' % k); w.save(P + 's%d.png' % k)
    ImageOps.mirror(w).save(P + 'm%d.png' % k); ImageOps.mirror(w).save(P + 't%d.png' % k)
    v = Image.open(P + 'v%d.png' % k).convert('RGBA')
    rv = w.height / v.height
    v = v.resize((round(v.width * rv), round(v.height * rv)), Image.LANCZOS)
    v.save(P + 'e%d.png' % k); ImageOps.mirror(v).save(P + 'f%d.png' % k)
    o.write('%d w %s（倍率 %.3f）e %s（倍率 %.3f）\n' % (k, w.size, rw, v.size, rv))
    tiles += [w, v]
th = 360
sc = th / max(t.height for t in tiles)
row = Image.new('RGBA', (sum(int(t.width * sc) + 20 for t in tiles) + 20, th + 40), (40, 40, 70, 255))
x = 20
for t in tiles:
    t2 = t.resize((int(t.width * sc), int(t.height * sc)), Image.LANCZOS)
    row.alpha_composite(t2, (x, 20 + th - t2.height)); x += t2.width + 20
row.convert('RGB').save(D + 'contact_move.png')
o.close()
