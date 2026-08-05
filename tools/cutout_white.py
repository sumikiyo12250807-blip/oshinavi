# -*- coding: utf-8 -*-
"""白背景のキャラ画像を切り抜いて、拡大まで済ませる。

grabCut（[[tools/odoku3_cutout.py]]）はグレー背景用。白背景なら「外側から白を塗りつぶす」
floodFillのほうが確実で速い（髪の毛の暗い部分を巻き込まない）。

シートの1カットは200px前後しかないので、動画に使う前にここで拡大する。
拡大はLANCZOS＋アンシャープ（ぼやけたまま渡すと出力までぼやける）。
"""
import argparse
import os

import cv2
import numpy as np


def cutout_white(path, thr=238):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 外周から白いところを塗って「外側の白」だけを背景にする（服の白い光沢を巻き込まない）
    flood = np.zeros((h + 2, w + 2), np.uint8)
    bg = np.zeros((h, w), np.uint8)
    for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        m = np.zeros((h + 2, w + 2), np.uint8)
        tmp = gray.copy()
        cv2.floodFill(tmp, m, seed, 0, loDiff=255 - thr, upDiff=255 - thr,
                      flags=4 | (255 << 8) | cv2.FLOODFILL_MASK_ONLY)
        bg |= m[1:-1, 1:-1]

    # 外周から届かない「閉じた白」も抜く＝腕と腰の間の三角形など。
    # 白い塊のうち面積が大きいものだけ背景に足す（目の白目や歯は小さいので残る）。
    white = (gray >= thr).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(white, 8)
    min_area = max(int(h * w * 0.0008), 30)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            bg[lab == i] = 255

    alpha = 255 - bg
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    alpha = cv2.GaussianBlur(alpha, (0, 0), 0.8)
    out = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    out[:, :, 3] = alpha
    return out, float((alpha > 128).mean())


def upscale(rgba, factor):
    if factor <= 1:
        return rgba
    h, w = rgba.shape[:2]
    big = cv2.resize(rgba, (int(w * factor), int(h * factor)), interpolation=cv2.INTER_LANCZOS4)
    # アンシャープ＝拡大でなまった輪郭を戻す（かけすぎると輪郭が硬くなる）
    rgb = big[:, :, :3].astype(np.float32)
    blur = cv2.GaussianBlur(rgb, (0, 0), 2.0)
    sharp = np.clip(rgb + (rgb - blur) * 0.6, 0, 255).astype(np.uint8)
    big[:, :, :3] = sharp
    return big


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--thr", type=int, default=238)
    ap.add_argument("--scale", type=float, default=1.0)
    args = ap.parse_args()

    rgba, ratio = cutout_white(args.src, args.thr)
    rgba = upscale(rgba, args.scale)
    cv2.imwrite(args.out, rgba)
    print("%s  前景率 %.1f%%  %dx%d" % (args.out, ratio * 100, rgba.shape[1], rgba.shape[0]))

    chk = args.out.replace(".png", "_onwhite.png")
    a = rgba[:, :, 3:4].astype(np.float32) / 255.0
    dark = np.zeros(rgba[:, :, :3].shape, np.uint8)
    cv2.imwrite(chk, (rgba[:, :, :3] * a + dark * (1 - a)).astype(np.uint8))
    print(chk)


main()
