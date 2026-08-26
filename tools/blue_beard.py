# -*- coding: utf-8 -*-
"""キャラの髭を「青髭」に染める（口の中・唇・肌は守る）。

  python tools/blue_beard.py --src tmp/promo/char.png --out tmp/promo/char_blue.png

やっていること＝指定した口まわりの矩形の中だけを見て、
「肌より暗くて・彩度が低めの茶色」＝髭の画素だけを青灰色へ寄せる。
唇や口の中は赤みが強い（R-Bが大きい）ので除外、歯や肌は明るいので除外。
"""
import io, sys, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--box", default="330,390,560,580", help="x0,y0,x1,y1（髭のある範囲）")
    ap.add_argument("--vmax", type=int, default=205, help="これより明るい画素は肌/歯として除外")
    ap.add_argument("--vmin", type=int, default=55, help="これより暗い画素は輪郭線として除外")
    ap.add_argument("--rb", type=int, default=95, help="R-Bがこれ以上＝唇/口の中とみなして除外")
    ap.add_argument("--mix", type=float, default=0.85, help="青へ寄せる強さ 0〜1")
    ap.add_argument("--exclude", default="", help="染めない矩形 x0,y0,x1,y1 を;区切りで（口の中など）")
    ap.add_argument("--probe", help="確認用に拡大画像も書き出す")
    a = ap.parse_args()

    im = Image.open(a.src).convert("RGBA")
    arr = np.array(im).astype(np.int16)
    x0, y0, x1, y1 = [int(v) for v in a.box.split(",")]

    reg = arr[y0:y1, x0:x1, :]
    r, g, b, al = reg[..., 0], reg[..., 1], reg[..., 2], reg[..., 3]
    v = np.maximum(np.maximum(r, g), b)

    beard = (al > 200) & (v <= a.vmax) & (v >= a.vmin) & ((r - b) < a.rb) & (r >= g) & (g >= b)

    # 口の中・歯など「髭ではないのに条件に合う所」を矩形で外す
    for box in [s for s in a.exclude.split(";") if s.strip()]:
        ex0, ey0, ex1, ey1 = [int(t) for t in box.split(",")]
        beard[max(0, ey0 - y0):max(0, ey1 - y0), max(0, ex0 - x0):max(0, ex1 - x0)] = False

    lum = (0.299 * r + 0.587 * g + 0.114 * b)
    # 同じ明るさのまま色相だけ青へ（青髭＝寒色の剃り跡）
    nr = np.clip(lum * 0.72, 0, 255)
    ng = np.clip(lum * 0.86, 0, 255)
    nb = np.clip(lum * 1.18 + 14, 0, 255)

    m = a.mix
    reg[..., 0] = np.where(beard, r * (1 - m) + nr * m, r)
    reg[..., 1] = np.where(beard, g * (1 - m) + ng * m, g)
    reg[..., 2] = np.where(beard, b * (1 - m) + nb * m, b)
    arr[y0:y1, x0:x1, :] = reg

    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    out.save(a.out)
    print("青髭に塗った画素 %d 個（範囲 %s） → %s" % (int(beard.sum()), a.box, a.out))

    if a.probe:
        pw = (x1 - x0) * 3
        ph = (y1 - y0) * 3
        out.crop((x0 - 60, y0 - 60, x1 + 60, y1 + 60)).resize((pw, ph)).save(a.probe)
        print("確認用 → %s" % a.probe)


if __name__ == "__main__":
    main()
