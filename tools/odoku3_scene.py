# -*- coding: utf-8 -*-
"""新お毒姐さん(黒スパンコール/紫の羽)のカットを、口パク動画用のシーン画像に仕立てる。
キャラシートの1カットは350x510しかないので拡大し、9:16の縦キャンバスに置く。
  python tools/odoku3_scene.py --cut tmp/char3/up_1.png --out tmp/char3/scene_up1.png
memory: project_odoku_x_video（参照は大きい絵が正しい。これは無料の試作用の暫定）
"""
import argparse
import os

from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ap = argparse.ArgumentParser()
ap.add_argument('--cut', default=os.path.join(REPO, 'tmp', 'char3', 'up_1.png'))
ap.add_argument('--out', default=os.path.join(REPO, 'tmp', 'char3', 'scene_up1.png'))
ap.add_argument('--width', type=int, default=1080)
ap.add_argument('--height', type=int, default=1920)
ap.add_argument('--bg', default='#1b0f2b')          # 暗い紫
ap.add_argument('--scale', type=float, default=0.0)  # 0=幅いっぱいに合わせる
a = ap.parse_args()

src = Image.open(a.cut).convert('RGB')
sw, sh = src.size
scale = a.scale if a.scale > 0 else a.width / sw
nw, nh = int(sw * scale), int(sh * scale)
src = src.resize((nw, nh), Image.LANCZOS)

canvas = Image.new('RGB', (a.width, a.height), a.bg)
x = (a.width - nw) // 2
y = (a.height - nh) // 2
canvas.paste(src, (x, y))
canvas.save(a.out)
print('%s  元%dx%d → %.2f倍 → %dx%d を (%d,%d) に配置 → キャンバス %dx%d'
      % (a.out, sw, sh, scale, nw, nh, x, y, a.width, a.height))
