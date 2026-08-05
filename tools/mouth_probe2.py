# -*- coding: utf-8 -*-
"""口の位置を目で確かめる汎用プローブ。指定した矩形を切って拡大し、10px目盛りを引く。
座標を勘で決めない（memory: feedback_no_speculation）。
  python tools/mouth_probe2.py --src tmp/char3/scene_up1.png --box 300,640,520,800 --out tmp/char3/probe.png
"""
import argparse
import os

from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument('--src', required=True)
ap.add_argument('--box', required=True, help='x0,y0,x1,y1')
ap.add_argument('--out', required=True)
ap.add_argument('--zoom', type=float, default=4.0)
a = ap.parse_args()

x0, y0, x1, y1 = [int(v) for v in a.box.split(',')]
im = Image.open(a.src).convert('RGB').crop((x0, y0, x1, y1))
z = a.zoom
im = im.resize((int(im.width * z), int(im.height * z)), Image.LANCZOS)
d = ImageDraw.Draw(im)

# 元画像座標で10pxごとに目盛り（20px毎に数値）
for gx in range(x0 - x0 % 10, x1 + 1, 10):
    px = int((gx - x0) * z)
    big = (gx % 50 == 0)
    d.line([(px, 0), (px, 14 if big else 7)], fill=(0, 255, 255), width=1)
    if big:
        d.text((px + 2, 14), str(gx), fill=(0, 255, 255))
for gy in range(y0 - y0 % 10, y1 + 1, 10):
    py = int((gy - y0) * z)
    big = (gy % 50 == 0)
    d.line([(0, py), (14 if big else 7, py)], fill=(0, 255, 0), width=1)
    if big:
        d.text((16, py + 2), str(gy), fill=(0, 255, 0))

im.save(a.out)
print('%s  元の範囲 x %d-%d / y %d-%d を %.1f倍 → %dx%d' % (a.out, x0, x1, y0, y1, z, im.width, im.height))
