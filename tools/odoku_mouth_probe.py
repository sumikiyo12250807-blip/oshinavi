# -*- coding: utf-8 -*-
"""口パクを作る前に、口がどこにあるかを目で確かめるための切り出し。

座標を勘で決めない（[[feedback_no_speculation]]）。切って見て、合うまで直す。
"""
import os

import cv2

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "tmp", "char", "odoku2_on_x.png")
OUT = os.path.join(REPO, "tmp", "char", "probe_mouth.png")

img = cv2.imread(SRC, cv2.IMREAD_UNCHANGED)
h, w = img.shape[:2]
print("src %dx%d" % (w, h))

# 顔まわりをざっくり切って拡大（比率で指定）
x0, x1 = int(w * 0.30), int(w * 0.70)
y0, y1 = int(h * 0.30), int(h * 0.50)
crop = img[y0:y1, x0:x1]
crop = cv2.resize(crop, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
cv2.imwrite(OUT, crop)
print("crop x %d-%d  y %d-%d  → %s" % (x0, x1, y0, y1, OUT))
