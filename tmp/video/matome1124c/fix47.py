# -*- coding: utf-8 -*-
# 女子プロレス w4 とボクサー w7 はシートでくっついていた（プロレスのブーツ＝シート y 669・ボクサーの髪＝y 676〜）
#   w4：シート y 673 より下（ボクサーの頭の縁取りの線のかけら）を消す
#   w7：シートの左の列（x 0〜505）・y 673 より下の alpha を全部ボクサーのものにする（左下の髪の先が w4 側に取られていた）→ いちばん大きい塊＋そばの塊
import numpy as np
import cv2
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
src = Image.open(D + 'sheet_n.png').convert('RGBA')
rgba = np.asarray(src).copy()
A = rgba[:, :, 3].astype(np.int32)
mx = max(1, int(np.percentile(A[A > 0], 99)))
A2 = np.clip(A * 255 // mx, 0, 255).astype(np.uint8)
SPLIT = 673
# w4
x0, y0 = 62, 342
w4 = Image.open(D + 'poses/w4.png').convert('RGBA')
a4 = np.asarray(w4).copy()
a4[max(0, SPLIT - y0):, :, 3] = 0
ys, xs = np.where(a4[:, :, 3] > 20)
Image.fromarray(a4).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(D + 'poses/w4.png')
# w7
reg = np.zeros(A2.shape, np.uint8)
reg[SPLIT:, :506] = (A2[SPLIT:, :506] > 40)
n, lab, st, _ = cv2.connectedComponentsWithStats(reg, 8)
big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
near = cv2.dilate((lab == big).astype(np.uint8), np.ones((41, 41), np.uint8)) > 0
keep = [j for j in range(1, n) if j == big or (near & (lab == j)).any()]
mine = cv2.dilate(np.isin(lab, keep).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
mine[:SPLIT, :] = False
mine[:, 506:] = False
al = np.where(mine, A2, 0).astype(np.uint8)
ys, xs = np.where(al > 20)
out = rgba.copy(); out[:, :, 3] = al
Image.fromarray(out).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(D + 'poses/w7.png')
open(D + 'fix47.txt', 'w', encoding='utf-8').write('w4 %s / w7 シート上 (%d, %d, %d, %d)\n' % (w4.size, xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
