# -*- coding: utf-8 -*-
"""X投稿の画面を背景に、お毒姐さんを右下に置いた1枚を作る（動画の元絵）。

ユーザー案（2026-08-02決定・2026-08-04に新キャラで再開）＝
「背景＝X投稿をくっきり見せる／お毒姐さんは右下に小さめ＝解説役。
  大きすぎると投稿の字が見えない・小さいほうが可愛い」

使い方:
  python tools/x_scene.py --bg tmp/video/bg_0805.png --char tmp/char3/cutout_full1.png \
      --out tmp/video/scene_0805.png --char-h 760
"""
import argparse
import os

import cv2
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bg", required=True)
    ap.add_argument("--char", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--char-h", type=int, default=760, help="キャラの高さ(px)")
    ap.add_argument("--align", default="right", choices=["right", "center", "left"])
    ap.add_argument("--right", type=int, default=40, help="右端からの余白（align=rightの時）")
    ap.add_argument("--bottom", type=int, default=10, help="下端からの余白")
    ap.add_argument("--shadow", type=int, default=1, help="足元に影を落とす")
    args = ap.parse_args()

    bg = cv2.imread(args.bg, cv2.IMREAD_COLOR)
    ch = cv2.imread(args.char, cv2.IMREAD_UNCHANGED)
    if ch.shape[2] != 4:
        raise SystemExit("キャラは透過PNGじゃないと駄目よ")

    H, W = bg.shape[:2]
    scale = args.char_h / ch.shape[0]
    cw = max(int(round(ch.shape[1] * scale)), 1)
    ch = cv2.resize(ch, (cw, args.char_h), interpolation=cv2.INTER_LANCZOS4)

    if args.align == "center":
        x0 = (W - cw) // 2
    elif args.align == "left":
        x0 = args.right
    else:
        x0 = W - cw - args.right
    y0 = H - args.char_h - args.bottom
    if y0 < 0:
        raise SystemExit("キャラが高すぎて画面に入らないわ")
    x0 = max(x0, 0)

    out = bg.copy()

    # 足元の影＝背景に浮かないように
    if args.shadow:
        sh = np.zeros((H, W), np.uint8)
        cv2.ellipse(sh, (x0 + cw // 2, y0 + args.char_h - 8), (int(cw * 0.42), 18),
                    0, 0, 360, 255, -1)
        sh = cv2.GaussianBlur(sh, (0, 0), 12).astype(np.float32) / 255.0 * 0.55
        out = (out * (1 - sh[:, :, None])).astype(np.uint8)

    # 画面からはみ出す分は切る（顔を大きく見せたい時に下や横がはみ出るため）
    y1 = min(y0 + args.char_h, H)
    x1 = min(x0 + cw, W)
    sub = ch[: y1 - y0, : x1 - x0]
    roi = out[y0:y1, x0:x1]
    a = sub[:, :, 3:4].astype(np.float32) / 255.0
    out[y0:y1, x0:x1] = (sub[:, :, :3] * a + roi * (1 - a)).astype(np.uint8)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    cv2.imwrite(args.out, out)
    print("%s  キャラ %dx%d を (%d,%d) に配置" % (args.out, cw, args.char_h, x0, y0))


main()
