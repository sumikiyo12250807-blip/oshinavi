# -*- coding: utf-8 -*-
"""お毒姐さんの口を開けた絵を作る（口パクの素）。

やり方（2代目）＝口の合わせ目から下を **画像の幅いっぱい** で下に引き伸ばし、
合わせ目に口の中の楕円を描く。矩形で切り貼りすると境界の帯が見えて失敗したので、
継ぎ目が出ない「全幅ワープ」に変えた（2026-08-04）。

座標は probe（tools/odoku_mouth_probe.py）で実際に切って確かめた実測値。
"""
import os

import cv2
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 既定＝初代お毒姐さん（1080x1920 の元画像上で実測）。
# 🚨キャラを変えたら座標も変わるので、環境変数で上書きできるようにした（2026-08-05）。
#   ODOKU_SRC / ODOKU_MOUTH_CX / ODOKU_MOUTH_LINE / ODOKU_MOUTH_W
#   座標は必ず tools/mouth_probe2.py で切って確かめてから入れる（勘で決めない）。
SRC = os.environ.get("ODOKU_SRC") or os.path.join(REPO, "tmp", "char", "odoku2_on_x.png")

MOUTH_CX = int(os.environ.get("ODOKU_MOUTH_CX", 497))    # 口の中心x
MOUTH_LINE = int(os.environ.get("ODOKU_MOUTH_LINE", 788))  # 上唇と下唇の合わせ目y
MOUTH_W = int(os.environ.get("ODOKU_MOUTH_W", 84))       # 口の幅
MOUTH_INSIDE = (40, 18, 78)  # BGR＝口の中（暗い赤紫）


def open_mouth(img, d):
    """口を d px 開ける。d=0 なら元のまま。"""
    if d <= 0:
        return img.copy()
    h, w = img.shape[:2]
    out = img.copy()

    # 合わせ目から下を全幅で d px ぶん引き伸ばす（＝顎が下がる）
    lower = img[MOUTH_LINE:h]
    stretched = cv2.resize(lower, (w, (h - MOUTH_LINE) + d), interpolation=cv2.INTER_LINEAR)
    out[MOUTH_LINE:h] = stretched[: h - MOUTH_LINE]

    # 口の中（楕円）。幅は口より少し狭く、高さは開き量に比例
    ax = int(MOUTH_W * 0.42)
    ay = max(int(d * 0.55), 3)
    overlay = out.copy()
    cv2.ellipse(overlay, (MOUTH_CX, MOUTH_LINE + d // 2), (ax, ay), 0, 0, 360, MOUTH_INSIDE, -1)
    # 縁を馴染ませる
    mask = np.zeros((h, w), np.uint8)
    cv2.ellipse(mask, (MOUTH_CX, MOUTH_LINE + d // 2), (ax, ay), 0, 0, 360, 255, -1)
    mask = cv2.GaussianBlur(mask, (0, 0), 2.5).astype(np.float32) / 255.0
    mask = mask[:, :, None]
    out = (overlay * mask + out * (1 - mask)).astype(np.uint8)
    return out


def main():
    img = cv2.imread(SRC, cv2.IMREAD_UNCHANGED)
    if img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    outdir = os.path.join(REPO, "tmp", "char", "mouth")
    os.makedirs(outdir, exist_ok=True)
    tiles = []
    for d in [0, 10, 20, 30]:
        f = open_mouth(img, d)
        cv2.imwrite(os.path.join(outdir, "open_%02d.png" % d), f)
        tiles.append(f[620:900, 380:620])
    cv2.imwrite(os.path.join(outdir, "compare.png"), np.hstack(tiles))
    print("wrote", outdir)


main()
