# -*- coding: utf-8 -*-
# cut_w.py：最後に「本体から離れた小さなかけら（600 点未満）で、ほかの子の分のそば（8 画素）にあるもの」を消す＝上の段のくつのかかとの細い弧（11/12 c6・c9 の頭の上）
import io
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
s = io.open(D + 'cut_w.py', encoding='utf-8').read()
a = "    ys, xs = np.where(al > 20)\n"
assert a in s and 'SPECK' not in s
s = s.replace(a, """    # SPECK
    oth = cv2.dilate(((OWN > 0) & (OWN != k)).astype(np.uint8), np.ones((17, 17), np.uint8)) > 0
    n6, l6, s6, _c6 = cv2.connectedComponentsWithStats((al > 20).astype(np.uint8), 8)
    if n6 > 1:
        bigc = 1 + int(np.argmax(s6[1:, cv2.CC_STAT_AREA]))
        for j in range(1, n6):
            if j != bigc and s6[j, cv2.CC_STAT_AREA] < 600 and (oth & (l6 == j)).any():
                al[l6 == j] = 0
                log.write('  %s%d かけらを消した %d 点 (%d,%d)\\n' % (PX, k, s6[j, cv2.CC_STAT_AREA], s6[j, 0], s6[j, 1]))
""" + a, 1)
io.open(D + 'cut_w.py', 'w', encoding='utf-8').write(s)
print('ok')
