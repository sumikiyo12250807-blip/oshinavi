# -*- coding: utf-8 -*-
# ニューヨーク・ちびガールズのシートの9人の箱を、白（と薄い市松）でない所のつながりで測る → boxes.txt
import io
import numpy as np
import cv2
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
out = []
a = np.asarray(Image.open(D + 'sheet.png').convert('RGB')).astype(int)
neu = (a.max(axis=2) - a.min(axis=2) < 10)
lum = a.sum(axis=2) / 3
out.append('明るさの分布（無彩色の所）: ' + str(np.percentile(lum[neu], [5, 25, 50, 75, 95]).round()))
fg = ~(neu & (lum >= 225))
fg = cv2.morphologyEx(fg.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
fgd = cv2.dilate(fg, np.ones((9, 9), np.uint8))
n, lab, st, cen = cv2.connectedComponentsWithStats(fgd, 8)
big = sorted([j for j in range(1, n) if st[j, 4] > 3000], key=lambda j: -st[j, 4])
out.append('塊 %d（>3000）' % len(big))
for j in sorted(big, key=lambda j: (int(cen[j][1] // 340), cen[j][0])):
    x, y, w, h, ar = st[j]
    out.append('  x%d-%d y%d-%d 面積 %d 中心 (%d,%d)' % (x, x + w, y, y + h, ar, cen[j][0], cen[j][1]))
col = fg.sum(axis=0); row = fg.sum(axis=1)
out.append('  列の空き ' + ' '.join('%d' % x for x in range(0, a.shape[1], 8) if col[x] == 0))
out.append('  行の空き ' + ' '.join('%d' % y for y in range(0, a.shape[0], 8) if row[y] == 0))
# 行ごとの前景の少ない所（段の切れ目の候補）
for y0, y1 in ((280, 420), (620, 760)):
    seg = row[y0:y1]
    out.append('  段の切れ目候補 %d〜%d: 最小 %d at %d' % (y0, y1, seg.min(), y0 + int(seg.argmin())))
io.open(D + 'boxes.txt', 'w', encoding='utf-8').write('\n'.join(out))
