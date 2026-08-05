# -*- coding: utf-8 -*-
"""新キャラをグレー背景から抜いて透過PNGにする。

背景に置く投稿画面を見せたいので、キャラは切り抜きが要る（[[project_odoku_x_video]]の
ユーザー案＝背景＝X投稿をくっきり／キャラは小さめの解説役）。
grabCut＝周囲を背景とみなして前景を推定する手法。旧キャラも同じやり方で抜いた。
"""
import argparse
import os

import cv2
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cutout(path, margin=0.06, iters=6):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    h, w = img.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    mx, my = int(w * margin), int(h * margin)
    rect = (mx, my, w - mx * 2, h - my * 2)
    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)
    cv2.grabCut(img, mask, rect, bgd, fgd, iters, cv2.GC_INIT_WITH_RECT)
    m = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype("uint8")
    # небольшой整形＝穴を埋めて縁を1px滑らかに
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    m = cv2.GaussianBlur(m, (0, 0), 1.0)
    out = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    out[:, :, 3] = m
    return out, float((m > 128).mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(REPO, "tmp", "char3", "full_1.png"))
    ap.add_argument("--out", default=os.path.join(REPO, "tmp", "char3", "cutout.png"))
    ap.add_argument("--margin", type=float, default=0.06)
    args = ap.parse_args()

    rgba, ratio = cutout(args.src, args.margin)
    cv2.imwrite(args.out, rgba)
    print("%s  前景率 %.1f%%  %dx%d" % (args.out, ratio * 100, rgba.shape[1], rgba.shape[0]))
    # 確認しやすいように白背景に載せた版も出す
    chk = args.out.replace(".png", "_onwhite.png")
    a = rgba[:, :, 3:4].astype(np.float32) / 255.0
    white = np.full(rgba[:, :, :3].shape, 255, np.uint8)
    cv2.imwrite(chk, (rgba[:, :, :3] * a + white * (1 - a)).astype(np.uint8))
    print(chk)


main()
