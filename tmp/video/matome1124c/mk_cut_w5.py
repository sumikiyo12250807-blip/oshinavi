# -*- coding: utf-8 -*-
# cut_w.py：行の切れ目の上下 30 画素の帯の中だけ、ある子の分のうち「細い所（7×7 で開くと消える）で、ほかの子の分から 6 画素以内」をそのほかの子へ移す
#   （上の段のくつ底の細い弧が下の段の子の頭に付いていた＝c6・c9）
import io
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
s = io.open(D + 'cut_w.py', encoding='utf-8').read()
a = "# GIVEBACK：細い弧を持ち主へ返す\n"
assert a in s and 'BANDFIX' not in s
s = s.replace(a, """# BANDFIX
BAND = np.zeros((H, W), bool)
for rr in R[1:3]:
    BAND[max(0, rr - 30):rr + 30] = True
for _ in range(3):
    for k in range(1, 10):
        mk_ = (OWN == k).astype(np.uint8)
        op = cv2.morphologyEx(mk_, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0
        thin = (mk_ > 0) & ~op & BAND
        if not thin.any():
            continue
        best = None
        for v in range(1, 10):
            if v == k:
                continue
            nv = cv2.dilate((OWN == v).astype(np.uint8), np.ones((13, 13), np.uint8)) > 0
            mv = thin & nv
            if mv.sum() > 5:
                OWN[mv] = v
                log.write('帯の細い所 %d → %d （%d 点）\\n' % (k, v, int(mv.sum())))
""" + a, 1)
io.open(D + 'cut_w.py', 'w', encoding='utf-8').write(s)
print('ok')
