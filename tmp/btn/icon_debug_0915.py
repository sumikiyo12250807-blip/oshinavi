# -*- coding: utf-8 -*-
"""アイコンを探す範囲の中の「光っている塊」を書き出す（2026-09-15 夜・うちわと観戦グッズでアイコンが消えた原因調べ）
使い方: python icon_debug_0915.py <元画像> <x0> <枠の上> <枠の下> <出力.png>
・範囲＝x0 から右端まで・枠の上下の線の外まで（btn_from_cd_0915 と同じ）
・max>200 の塊ごとに 位置・大きさ・面積・範囲の端に触れているか を出す（面積200以上だけ）
・切り抜きを出力.png に保存（縦を 400 に縮める）
"""
import sys
import numpy as np
import cv2
from PIL import Image

path, x0, ft, fb, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
im = np.asarray(Image.open(path).convert('RGB'))
y0, y1 = max(0, ft - 10), min(im.shape[0], fb + 11)
sub = im[y0:y1, x0:]
h, w = sub.shape[:2]
core = (sub.max(axis=2) > 200).astype(np.uint8)
n, lab, stats, _ = cv2.connectedComponentsWithStats(core, connectivity=8)
print('範囲 x %d〜%d y %d〜%d （%dx%d）' % (x0, im.shape[1], y0, y1, w, h))
for i in range(1, n):
    x, y, bw, bh, area = stats[i]
    if area < 200:
        continue
    touch = ''.join(s for s, t in (('左', x == 0), ('上', y == 0), ('右', x + bw >= w), ('下', y + bh >= h)) if t)
    print('塊%d x%d〜%d y%d〜%d 面積%d 端:%s' % (i, x0 + x, x0 + x + bw, y0 + y, y0 + y + bh, area, touch or 'なし'))
s = 400 / h
Image.fromarray(sub).resize((round(w * s), 400), Image.LANCZOS).save(out)
