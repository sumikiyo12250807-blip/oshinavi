# -*- coding: utf-8 -*-
# g5・g6 の頭の上に残った上の子のくつ（離れた塊）を消す＝いちばん大きい塊と、そこから 12px 以内の塊だけ残す
import io
import numpy as np
import cv2
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
log = []
for n in ('g5', 'g6'):
    im = Image.open(D + n + '.png').convert('RGBA')
    a = np.asarray(im).copy()
    m = (a[:, :, 3] > 20).astype(np.uint8)
    k, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    near = cv2.dilate((lab == big).astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
    keep = np.zeros_like(m, bool)
    for j in range(1, k):
        if j == big or (near & (lab == j)).any():
            keep |= lab == j
        else:
            log.append('%s 消した塊 %d 点 箱 %s' % (n, st[j, cv2.CC_STAT_AREA], tuple(st[j, :4])))
    keep = cv2.dilate(keep.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    a[:, :, 3] = np.where(keep, a[:, :, 3], 0)
    ys, xs = np.where(a[:, :, 3] > 20)
    Image.fromarray(a).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(D + n + '.png')
io.open(D + 'fix_g56.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
