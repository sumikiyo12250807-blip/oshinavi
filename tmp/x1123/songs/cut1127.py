# -*- coding: utf-8 -*-
# Downloads/cyberrap_chibi_1127c.png（3×3・背景透明）を9人に切る → poses/p1〜p9.png・cut1127.txt・poses/contact.png
import os, io
import numpy as np
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/x1123/songs/'
OUT = D + 'poses/'
os.makedirs(OUT, exist_ok=True)
src = Image.open('C:/Users/user/Downloads/cyberrap_chibi_1127c.png').convert('RGBA')
W, H = src.size
A = np.asarray(src)[:, :, 3]
log = io.open(D + 'cut1127.txt', 'w', encoding='utf-8')
def cut(prof, lo, hi):
    seg = np.convolve(prof[lo:hi].astype(float), np.ones(9) / 9, 'same')
    return lo + int(np.argmin(seg))
rowp, colp = (A > 40).sum(axis=1), (A > 40).sum(axis=0)
R = [0, cut(rowp, int(H * .25), int(H * .42)), cut(rowp, int(H * .58), int(H * .75)), H]
C = [0, cut(colp, int(W * .25), int(W * .42)), cut(colp, int(W * .58), int(W * .75)), W]
log.write('行 %s 列 %s\n' % (R, C))
n = 0
thumbs = []
for r in range(3):
    for c in range(3):
        n += 1
        cell = src.crop((C[c], R[r], C[c + 1], R[r + 1]))
        a = np.asarray(cell)[:, :, 3]
        ys, xs = np.where(a > 40)
        bb = (max(xs.min() - 4, 0), max(ys.min() - 4, 0), min(xs.max() + 5, cell.width), min(ys.max() + 5, cell.height))
        p = cell.crop(bb)
        edge = bb[0] == 0 or bb[1] == 0 or bb[2] == cell.width or bb[3] == cell.height
        p.save(OUT + 'p%d.png' % n)
        log.write('p%d %s 箱の端に触れた=%s\n' % (n, p.size, edge))
        t = Image.new('RGBA', (220, 300), (30, 30, 50, 255))
        q = p.copy(); q.thumbnail((210, 290))
        t.alpha_composite(q, ((220 - q.width) // 2, (300 - q.height) // 2))
        ImageDraw.Draw(t).text((6, 4), str(n), fill=(255, 255, 0, 255))
        thumbs.append(t)
sheet = Image.new('RGBA', (660, 900))
for i, t in enumerate(thumbs):
    sheet.paste(t, ((i % 3) * 220, (i // 3) * 300))
sheet.convert('RGB').save(OUT + 'contact.png')
