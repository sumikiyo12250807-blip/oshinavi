# -*- coding: utf-8 -*-
"""お毒姐さん（2026-08-04確定版・紫スパンコール／白背景／表情16種）のシートを分割する。

シート構成（704×1524）:
  1段目 全身4面（正面/斜め/横/後ろ）
  2段目 顔アップ大・バストアップ大・横全身・後ろ全身
  3〜5段目 表情12種（各段4つ）
動画に使うのは2段目の「バストアップ大」。口が閉じていて正面寄りだから口パクの元になる。
座標は切ってから目で確かめる（勘で決めない）。
"""
import os

import cv2
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "tmp", "char5")
img = cv2.imread(os.path.join(D, "sheet.png"))
h, w = img.shape[:2]
print("sheet %dx%d" % (w, h))

# 比率で切る（元画像が差し替わっても効くように）
CUTS = {
    # 腰に手を当てて横に広がるので、見た目より幅を取る（0.245だと右腕が切れた）
    "full_front": (0.020, 0.005, 0.355, 0.325),   # 1段目いちばん左＝正面全身
    "face_big":   (0.000, 0.325, 0.255, 0.545),   # 2段目左＝顔アップ
    "bust_big":   (0.255, 0.325, 0.520, 0.555),   # 2段目2番目＝バストアップ
}

for name, (rx0, ry0, rx1, ry1) in CUTS.items():
    x0, x1 = int(w * rx0), int(w * rx1)
    y0, y1 = int(h * ry0), int(h * ry1)
    crop = img[y0:y1, x0:x1]
    p = os.path.join(D, name + ".png")
    cv2.imwrite(p, crop)
    print("%-11s %dx%d" % (name, crop.shape[1], crop.shape[0]))

# 表情12種も後で使えるように3〜5段目を4分割で切っておく
rows = [(0.560, 0.705), (0.710, 0.855), (0.860, 1.000)]
n = 0
for ri, (ry0, ry1) in enumerate(rows):
    for ci in range(4):
        x0, x1 = int(w * ci / 4), int(w * (ci + 1) / 4)
        y0, y1 = int(h * ry0), int(h * ry1)
        n += 1
        cv2.imwrite(os.path.join(D, "exp_%02d.png" % n), img[y0:y1, x0:x1])
print("表情 %d枚" % n)
