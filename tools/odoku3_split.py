# -*- coding: utf-8 -*-
"""新しいお毒姐さん（2026-08-04版・黒髪ショート／紫の羽根）のキャラシートをバラす。

シートは上段4カット（バストアップ）＋下段6カット（全身）。切り出し座標は
画像の実寸から比率で出し、切ったあと目で確かめる（勘で決めない）。
"""
import os
import shutil

import cv2

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DL = r"C:\Users\user\Downloads\ChatGPT Image 2026年8月4日 11_16_26.png"
DST_DIR = os.path.join(REPO, "tmp", "char3")
SHEET = os.path.join(DST_DIR, "sheet.png")

os.makedirs(DST_DIR, exist_ok=True)
if not os.path.exists(SHEET):
    shutil.copyfile(SRC_DL, SHEET)

img = cv2.imread(SHEET, cv2.IMREAD_UNCHANGED)
h, w = img.shape[:2]
print("sheet %dx%d" % (w, h))

# 上段は横4等分、下段は横6等分。段の境目は縦の比率で
TOP_Y0, TOP_Y1 = 0, int(h * 0.455)
BOT_Y0, BOT_Y1 = int(h * 0.455), h

for i in range(4):
    x0 = int(w * i / 4)
    x1 = int(w * (i + 1) / 4)
    cv2.imwrite(os.path.join(DST_DIR, "up_%d.png" % (i + 1)), img[TOP_Y0:TOP_Y1, x0:x1])

for i in range(6):
    x0 = int(w * i / 6)
    x1 = int(w * (i + 1) / 6)
    cv2.imwrite(os.path.join(DST_DIR, "full_%d.png" % (i + 1)), img[BOT_Y0:BOT_Y1, x0:x1])

print("wrote", DST_DIR)
