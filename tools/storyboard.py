# -*- coding: utf-8 -*-
"""絵コンテ＝構図の候補を並べて1枚にする（作る前に見て決めるため）。

ユーザー方針（2026-08-04）＝「字は全部見えなくていい／動画を出すとき本文は別に載せる。
キャラは胸から上だけでいい」。だからキャラを大きく、背景の投稿は雰囲気として見える程度。
"""
import argparse
import os
import subprocess
import sys

import cv2
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 既定値。--bg / --char / --outdir で差し替えられる（2026-08-05 引数対応）
BG = os.path.join(REPO, "tmp", "video", "bg_0805.png")
CHAR = os.path.join(REPO, "tmp", "char5", "cutout_full.png")
OUTDIR = os.path.join(REPO, "tmp", "video", "storyboard")

# (名前, キャラの高さ, 寄せ, 下端の余白)
# ユーザー指定（2026-08-04）＝「この人は全身でいい。小さめに」
PLANS = [
    ("A_850_右", 850, "right", 0),
    ("B_700_右", 700, "right", 0),
    ("C_1000_右", 1000, "right", 0),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bg", default=BG)
    ap.add_argument("--char", default=CHAR)
    ap.add_argument("--outdir", default=OUTDIR)
    ap.add_argument("--heights", default="", help="キャラの高さをカンマ区切りで（例 700,850,1000）")
    a = ap.parse_args()
    plans = PLANS
    if a.heights:
        plans = [("%s_右" % h.strip(), int(h), "right", 0) for h in a.heights.split(",")]

    os.makedirs(a.outdir, exist_ok=True)
    tiles = []
    for name, h, align, bottom in plans:
        out = os.path.join(a.outdir, name + ".png")
        cmd = [sys.executable, os.path.join(REPO, "tools", "x_scene.py"),
               "--bg", a.bg, "--char", a.char, "--out", out,
               "--char-h", str(h), "--align", align, "--bottom", str(bottom),
               "--shadow", "0"]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        img = cv2.imread(out)
        t = cv2.resize(img, (350, 622), interpolation=cv2.INTER_AREA)
        cv2.rectangle(t, (0, 0), (349, 621), (60, 60, 60), 2)
        tiles.append(t)
        print(name, h, align)
    cv2.imwrite(os.path.join(a.outdir, "compare.png"), np.hstack(tiles))
    print(os.path.join(a.outdir, "compare.png"))


main()
