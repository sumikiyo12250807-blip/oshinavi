# -*- coding: utf-8 -*-
# cut_w.py に後処理を足す：分けた後、ある子の分のうち「細い線（開いて消える所）で本体から離れ、ほかの子のそば」にある所は、そのほかの子へ返す
#   （11/12 c1・c3 の足もとに下の段の子のベレー帽・髪のふちの細い弧が付き、下の子の頭のてっぺんが欠けていた）
import io
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
s = io.open(D + 'cut_w.py', encoding='utf-8').read()
a = "os.makedirs(D + 'poses', exist_ok=True)\n"
assert a in s and 'GIVEBACK' not in s
s = s.replace(a, """# GIVEBACK：細い弧を持ち主へ返す
for _ in range(2):
    for k in range(1, 10):
        mk_ = ((OWN == k) & (FG > 0)).astype(np.uint8)
        op = cv2.morphologyEx(mk_, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
        n4, l4, s4, _c4 = cv2.connectedComponentsWithStats(op, 8)
        if n4 <= 1:
            continue
        body = l4 == 1 + int(np.argmax(s4[1:, cv2.CC_STAT_AREA]))
        keep = cv2.dilate(body.astype(np.uint8), np.ones((13, 13), np.uint8)) > 0
        rest = (OWN == k) & ~keep
        if not rest.any():
            continue
        n5, l5 = cv2.connectedComponents(rest.astype(np.uint8), 8)
        for j in range(1, n5):
            pc = l5 == j
            ring = cv2.dilate(pc.astype(np.uint8), np.ones((21, 21), np.uint8)) > 0
            vs, cnt = np.unique(OWN[ring & (OWN > 0) & (OWN != k)], return_counts=True)
            if len(vs) and cnt.max() > 30:
                OWN[pc] = int(vs[np.argmax(cnt)])
                log.write('返した %d → %d （%d 点）\\n' % (k, int(vs[np.argmax(cnt)]), int(pc.sum())))
""" + a, 1)
io.open(D + 'cut_w.py', 'w', encoding='utf-8').write(s)
print('ok')
