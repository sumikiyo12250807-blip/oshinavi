# -*- coding: utf-8 -*-
"""キャラシートから正面立ち姿だけを切り出して参照画像にする。
シート全体を参照に渡すと文字やポーズ一覧まで学習素材になって崩れるため。
"""
import os
import glob
from PIL import Image

cands = glob.glob(os.path.join(os.path.expanduser("~"), "Downloads", "ChatGPT Image *22_18_11.png"))
if not cands:
    raise SystemExit("source image not found in Downloads")
SRC = cands[0]
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "char")

im = Image.open(SRC)
W, H = im.size
print("source size:", W, H)

# 吹き出し・キャプションの文字が入らない領域だけを使う
crops = {
    "odoku_front": (0.466, 0.048, 0.607, 0.306),  # いろんな角度の1体目（正面寄り全身）
    "odoku_smile": (0.868, 0.527, 0.993, 0.660),  # 表情バリエーション「笑い上戸」
    "odoku_pose":  (0.583, 0.737, 0.712, 0.942),  # ポーズ例2体目
}

MIN_SIDE = 640  # APIの下限256を余裕で超えるまで拡大する

os.makedirs(OUTDIR, exist_ok=True)
for name, (l, t, r, b) in crops.items():
    box = (int(W * l), int(H * t), int(W * r), int(H * b))
    piece = im.crop(box).convert("RGB")
    if min(piece.size) < MIN_SIDE:
        k = MIN_SIDE / min(piece.size)
        piece = piece.resize((round(piece.width * k), round(piece.height * k)), Image.LANCZOS)
    out = os.path.join(OUTDIR, name + ".png")
    piece.save(out)
    print(name, box, "->", piece.size, out, os.path.getsize(out), "bytes")
