# -*- coding: utf-8 -*-
"""ユーザーが作ったネオンのボタン画像から、枠（ピル）の部分だけを切り出して縮める（2026-09-14 夜）。
元の画像は周りに黒い余白と床の映り込みがあり、1.6MB。いまの img/btn_*.png（高さ88・40KB台）にそろえる。
・明るい画素（どれかの色が THR 以上）が行の3割以上ある行＝枠の中。いちばん長い続きの帯を枠とみなす（映り込みは暗いので外れる）
・列も同じ帯の中で数える
・周りに PAD 画素を残して切り、高さ 88 に縮めて保存
使い方: python crop_btn.py <入力.png> <出力.png>
"""
import sys
from PIL import Image

THR, PAD, H = 150, 6, 88
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
w, h = im.size
px = im.load()
bright = [[max(px[x, y]) >= THR for x in range(w)] for y in range(h)]
rows = [sum(r) >= w * 0.3 for r in bright]
best, cur, start = (0, 0), 0, 0
for y, ok in enumerate(rows + [False]):
    if ok:
        if cur == 0:
            start = y
        cur += 1
    else:
        if cur > best[1] - best[0]:
            best = (start, start + cur)
        cur = 0
y0, y1 = best
cols = [sum(bright[y][x] for y in range(y0, y1)) >= (y1 - y0) * 0.3 for x in range(w)]
xs = [x for x, ok in enumerate(cols) if ok]
x0, x1 = xs[0], xs[-1] + 1
box = (max(0, x0 - PAD), max(0, y0 - PAD), min(w, x1 + PAD), min(h, y1 + PAD))
out = im.crop(box)
nw = round(out.width * H / out.height)
out = out.resize((nw, H), Image.LANCZOS)
out.save(dst, optimize=True)
import os
print('元 %dx%d ｜切り出し %s ｜出力 %dx%d ｜%dKB' % (w, h, box, nw, H, os.path.getsize(dst) // 1024))
