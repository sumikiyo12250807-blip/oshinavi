# -*- coding: utf-8 -*-
"""ボタン画像を「枠の上下の線」で切り出して高さ88に縮める（2026-09-15 夜）。
9/14 の crop_btn_0914.py は「明るい行の続き」で切っていたため、文字の太い画像だと枠の線が欠けた（観戦グッズ・推し活グッズ・オペラグラス）。
・枠の線＝明るい水色（G>=190 かつ B>=220）が横幅の85%以上ある行。いちばん上と下の行を枠とみなす
・横は枠がほぼ端まであるので全幅
・上下に PAD 画素を残して切る
使い方: python crop_btn_frame_0915.py <入力.png> <出力.png> [<入力.png> <出力.png> ...]
"""
import os
import sys
from PIL import Image

PAD, H, FRAC = 12, 88, 0.85
args = sys.argv[1:]
for src, dst in zip(args[0::2], args[1::2]):
    im = Image.open(src).convert('RGB')
    w, h = im.size
    px = im.load()
    rows = []
    for y in range(h):
        n = sum(1 for x in range(0, w, 2) if px[x, y][1] >= 190 and px[x, y][2] >= 220)
        if n / (w / 2) >= FRAC:
            rows.append(y)
    y0, y1 = max(0, rows[0] - PAD), min(h, rows[-1] + 1 + PAD)
    out = im.crop((0, y0, w, y1))
    nw = round(out.width * H / out.height)
    out = out.resize((nw, H), Image.LANCZOS)
    out.save(dst, optimize=True)
    print('%s ｜枠 %d〜%d ｜出力 %dx%d ｜%dKB' % (os.path.basename(dst), rows[0], rows[-1], nw, H, os.path.getsize(dst) // 1024))
