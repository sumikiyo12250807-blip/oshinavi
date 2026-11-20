# -*- coding: utf-8 -*-
# fix47 の続き：w4（女子プロレス）の左下の髪の先が抜けていた＝シートの左の列（x 0〜511）・y 338〜672 の alpha を足す（今の w4 と合わせる）
#   w7（ボクサー）の頭の上に残った黒い線（プロレスのブーツの縁取り・シート y 673〜679 の暗い画素）を消す
import numpy as np
import cv2
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = Image.open(D + 'sheet_n.png').convert('RGBA')
rgba = np.asarray(src).copy()
A = rgba[:, :, 3].astype(np.int32)
mx = max(1, int(np.percentile(A[A > 0], 99)))
A2 = np.clip(A * 255 // mx, 0, 255).astype(np.uint8)
H, W = A2.shape
# w4：今の切り抜きをシートの上へ戻す（シート上の左上＝62, 342）
cur = np.asarray(Image.open(D + 'poses/w4.png').convert('RGBA'))[:, :, 3]
own = np.zeros((H, W), bool)
own[342:342 + cur.shape[0], 62:62 + cur.shape[1]] = cur > 20
reg = np.zeros((H, W), np.uint8)
reg[338:673, :512] = A2[338:673, :512] > 40
reg |= own.astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(reg, 8)
big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
near = cv2.dilate((lab == big).astype(np.uint8), np.ones((41, 41), np.uint8)) > 0
keep = [j for j in range(1, n) if j == big or (near & (lab == j)).any()]
mine = (cv2.dilate(np.isin(lab, keep).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0) | own
mine[:338] = False; mine[673:] = False; mine[:, 523:] = False
al = np.where(mine, A2, 0).astype(np.uint8)
ys, xs = np.where(al > 20)
out = rgba.copy(); out[:, :, 3] = al
Image.fromarray(out).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(D + 'poses/w4.png')
b4 = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
# w7：シート上の左上＝48, 673
w7 = np.asarray(Image.open(D + 'poses/w7.png').convert('RGBA')).copy()
for yy in range(0, 7):
    row = w7[yy]
    dark = row[:, :3].astype(int).sum(axis=1) < 200
    row[dark, 3] = 0
ys, xs = np.where(w7[:, :, 3] > 20)
Image.fromarray(w7).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(D + 'poses/w7.png')
open(D + 'fix47b.txt', 'w', encoding='utf-8').write('w4 シート上 %s / w7 上を %d 切った\n' % (b4, ys.min()))
