# -*- coding: utf-8 -*-
# w4/m4（エルフ）・a5/b5（森の子）の足もとに残った小さな点（下の段の子の縁取りのかけら）を消す
#   alpha>10 の塊のうち面積 400 未満で、いちばん大きい塊の下 15% にあるもの
import io
import numpy as np
import cv2
from PIL import Image
P = 'C:/Users/user/oshinavi/tmp/video/matome1124c/poses/'
out = []
for nm in ('w4', 'm4', 'a5', 'b5'):
    a = np.asarray(Image.open(P + nm + '.png')).copy()
    al = a[:, :, 3]
    H = al.shape[0]
    n, lab, st, _ = cv2.connectedComponentsWithStats((al > 10).astype(np.uint8), 8)
    big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    k = 0
    for j in range(1, n):
        if j != big and st[j, cv2.CC_STAT_AREA] < 400 and st[j, cv2.CC_STAT_TOP] > H * 0.85:
            al[lab == j] = 0
            k += 1
    a[:, :, 3] = al
    Image.fromarray(a).save(P + nm + '.png')
    out.append('%s 消した点 %d' % (nm, k))
io.open(P + '../speck14.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
