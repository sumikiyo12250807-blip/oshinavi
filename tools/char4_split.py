# -*- coding: utf-8 -*-
"""新キャラ（2026-08-04確定・紫髪＋金縁メガネ＋チャイナ服）のシートから使うカットを切り出す。

シートは704×1524と小さいので、いちばん大きく写っている
①上部のバストアップ ②下部の顔アップ の2枚だけを使う。
切ったら必ず目で確かめる（座標を勘で決めない）。
"""
import os

import cv2

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "tmp", "char4")
img = cv2.imread(os.path.join(D, "sheet.png"))
h, w = img.shape[:2]
print("sheet %dx%d" % (w, h))

CUTS = {
    # 名前: (x0, y0, x1, y1)
    # 右端はディテール枠への引き出し線が写り込むので 398 で切る
    "bust": (0, 15, 398, 515),        # 上部の大きいバストアップ
    "face": (22, 1072, 352, 1505),    # 下部の顔アップ
}

for name, (x0, y0, x1, y1) in CUTS.items():
    crop = img[y0:y1, x0:x1]
    p = os.path.join(D, name + ".png")
    cv2.imwrite(p, crop)
    print("%-6s %dx%d  %s" % (name, crop.shape[1], crop.shape[0], p))
