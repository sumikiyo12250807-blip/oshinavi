# -*- coding: utf-8 -*-
# w4（金のダンス）の下に、下の段のペンライトの子 w7 の頭の輪郭線（細い線）が付いてきた＝細い塊を落とす
#   開く（5px で削って戻す）と線は消える＝開いたあとに残る本体に触れない塊は落とす → poses/w4・m4 を上書き・look_w4b.png
import io
import numpy as np
import cv2
from PIL import Image, ImageOps
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
im = Image.open(D + 'poses/w4.png').convert('RGBA')
a = np.asarray(im).copy()
A = a[:, :, 3]
fg = (A > 10).astype(np.uint8)
opened = cv2.morphologyEx(fg, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
n, lab, st, _ = cv2.connectedComponentsWithStats(opened, 8)
big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
keep_core = cv2.dilate((lab == big).astype(np.uint8), np.ones((9, 9), np.uint8))
n2, lab2, st2, _ = cv2.connectedComponentsWithStats(fg, 8)
log = []
mask = np.zeros_like(fg)
for j in range(1, n2):
    comp = lab2 == j
    touch = (keep_core[comp] > 0).mean()
    ok = touch > 0.5
    log.append('塊 %d 面積 %d 箱 %s 本体に重なる %.2f %s' % (j, st2[j, cv2.CC_STAT_AREA], tuple(st2[j, :4]), touch, '残す' if ok else '落とす'))
    if ok:
        mask[comp] = 1
# 線は薄い alpha で本体とつながっていた＝「開いたあとの本体＋まわり 6px」だけ残す（髪の先は本体から 6px 以内）
keep2 = cv2.dilate((lab == big).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
log.append('開いた本体のまわりで落とした画素 %d' % int(((fg > 0) & (keep2 == 0)).sum()))
a[:, :, 3] = np.where((mask > 0) & (keep2 > 0), A, 0)
ys, xs = np.where(a[:, :, 3] > 20)
out = Image.fromarray(a).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
out.save(D + 'poses/w4.png')
ImageOps.mirror(out).save(D + 'poses/m4.png')
g = Image.new('RGBA', out.size, (0, 150, 60, 255)); g.alpha_composite(out)
k = 700 / g.height
g.convert('RGB').resize((int(g.width * k), 700), Image.LANCZOS).save(D + 'look_w4b.png')
log.append('新しい大きさ %s' % (out.size,))
io.open(D + 'fix_w4.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
