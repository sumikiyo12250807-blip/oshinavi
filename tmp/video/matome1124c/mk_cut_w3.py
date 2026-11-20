# -*- coding: utf-8 -*-
# cut_w.py：くっついた塊の分け方を「平らな絵の watershed」から「塊の中だけで種から1画素ずつ広げる」に替える
#   （平らな watershed は塊の外の印 99 が縁から内へ流れ込み、細い手・ブーツ・髪の先を落としていた＝11/12 c9）
import io
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
s = io.open(D + 'cut_w.py', encoding='utf-8').read()
a = s.index("        flat = np.full((H, W, 3), 128, np.uint8)")
b = s.index("        OWN[edge] = ks[0]\n") + len("        OWN[edge] = ks[0]\n")
s = s[:a] + """        lab_ = np.where(comp, np.where(mk == 99, 0, mk), 0).astype(np.int32)
        ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        for _it in range(2000):
            free = comp & (lab_ == 0)
            if not free.any():
                break
            ch = False
            for v in ks:
                g = (cv2.dilate((lab_ == v).astype(np.uint8), ker) > 0) & free
                if g.any():
                    lab_[g] = v; free &= ~g; ch = True
            if not ch:
                break
        for v in ks:
            OWN[comp & (lab_ == v)] = v
""" + s[b:]
io.open(D + 'cut_w.py', 'w', encoding='utf-8').write(s)
print('ok')
