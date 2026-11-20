# -*- coding: utf-8 -*-
# 11/7 すちこの直し（20:07「日本人はお辞儀で始まってお辞儀で終わる」）
#   ①k5（ピンクのお団子・正座でお辞儀）をシートから切り直す＝k2 のぞうりの底（y≦405・x 595〜712）だけ k2 に渡し、その下の髪は全部 k5
#   ②k2 もシートから切り直す（y≦405 で切る＝k5 の髪の線が残らない）
#   ③並び＝頭 k4・締め k5。2巡目の n4（お辞儀）は締めの k5 と似る＝n3（ウインクで指さしの反転）に替える。後奏は残り8人で2段
import io, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
import numpy as np, cv2
from PIL import Image, ImageOps, ImageDraw
out = io.open(D + 'prep1107f.txt', 'w', encoding='utf-8')
s = Image.open(D + 'sheet_k.png').convert('RGBA')
A = np.asarray(s).copy()
al = A[:, :, 3].astype(np.int32)
mx = max(1, int(np.percentile(al[al > 0], 99)))
A2 = np.clip(al * 255 // mx, 0, 255).astype(np.uint8)
H, W = A2.shape
yy, xx = np.mgrid[0:H, 0:W]


def cut(region, name):
    m = (A2 > 40) & region
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), 8)
    big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    near = cv2.dilate((lab == big).astype(np.uint8), np.ones((41, 41), np.uint8)) > 0
    keep = np.zeros_like(m)
    for j in range(1, n):
        if j == big or (st[j, cv2.CC_STAT_AREA] > 30 and (near & (lab == j)).any()):
            keep |= lab == j
    keep = (cv2.dilate(keep.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & region
    o = A.copy()
    o[:, :, 3] = np.where(keep, A2, 0)
    ys, xs = np.where(o[:, :, 3] > 20)
    bb = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    im = Image.fromarray(o).crop(bb)
    im.save(D + 'poses/%s.png' % name)
    out.write('%s 大きさ %s シート上 %s\n' % (name, im.size, bb))
    return im, bb


sole = (yy <= 405) & (xx >= 595) & (xx <= 712)
k5, b5 = cut((xx >= 400) & (xx <= 805) & (yy >= 380) & (yy <= 830) & ~sole, 'k5')
k2, b2 = cut((xx >= 430) & (xx <= 800) & (yy <= 405), 'k2')
ImageOps.mirror(k2).save(D + 'poses/n2.png')
ImageOps.mirror(Image.open(D + 'poses/k3.png')).save(D + 'poses/n3.png')
if os.path.exists(D + 'k5_unused.png'):
    os.remove(D + 'k5_unused.png')
# 等倍で見る：元の絵（緑の地）と切り抜き（灰色の地）
flat = Image.alpha_composite(Image.new('RGBA', s.size, (0, 140, 0, 255)), s).convert('RGB')
rows = []
for im, bb in ((k5, b5), (k2, b2)):
    o = flat.crop((bb[0] - 20, max(0, bb[1] - 20), bb[2] + 20, min(H, bb[3] + 20)))
    g = Image.new('RGB', (im.width + 40, im.height + 40), (120, 120, 120)); g.paste(im, (20, 20), im)
    r = Image.new('RGB', (o.width + g.width + 20, max(o.height, g.height)), (20, 20, 20))
    r.paste(o, (0, 0)); r.paste(g, (o.width + 20, 0)); rows.append(r)
L = Image.new('RGB', (max(r.width for r in rows), sum(r.height + 10 for r in rows)), (20, 20, 20))
y = 0
for r in rows:
    L.paste(r, (0, y)); y += r.height + 10
L.save(D + 'poses/look_k5_k2.png')
# 並び
r = io.open(D + 'render.py', encoding='utf-8').read()
r, n = re.subn(r"ORDER = \['k1'[^\n]*\n",
               "ORDER = ['k4', 'k1', 'k7', 'k6', 'k2', 'k8', 'k9', 'n6', 'n1', 'n3', 'n8', 'n9', 'n7', 'n2', 'k5']   # 11/7 すちこ「お辞儀で始まってお辞儀で終わる」＝頭 k4・締め k5（正座でお辞儀）／2巡目は左右反転 n・n4 は締めと似るので n3\n", r)
assert n == 1
for a, b in (("'names': ['k1', 'k4', 'k7', 'k6', 'k2', 'k8', 'k9'],", "'names': ['k4', 'k1', 'k7', 'k6', 'k2', 'k8', 'k9', 'k3'],"),
             ("_rows = [(135 + 270 * i, 1190, 250) for i in range(4)] + [(270 + 270 * i, 1470, 250) for i in range(3)]",
              "_rows = [(135 + 270 * i, 1190, 250) for i in range(4)] + [(135 + 270 * i, 1470, 250) for i in range(4)]")):
    assert a in r, a
    r = r.replace(a, b)
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)
p = subprocess.run([sys.executable, D + 'render.py', '--frames', '2.0,104.0,118.0,138.5'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
out.write('frames rc %s %s %s\n' % (p.returncode, p.stdout[-600:], p.stderr[-1500:]))
out.close()
