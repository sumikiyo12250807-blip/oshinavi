# -*- coding: utf-8 -*-
"""ボタン画像の行ごとの「明るい水色の画素」の割合を出して、枠の上下の線がどこにあるかを見る（2026-09-15 夜）。
使い方: python btn_profile_0915.py <入力.png>
"""
import sys
from PIL import Image

im = Image.open(sys.argv[1]).convert('RGB')
w, h = im.size
px = im.load()
for y in range(0, h, 4):
    n = sum(1 for x in range(0, w, 2) if px[x, y][1] >= 190 and px[x, y][2] >= 220)
    f = n / (w / 2)
    if f >= 0.4:
        print(y, round(f, 2))
