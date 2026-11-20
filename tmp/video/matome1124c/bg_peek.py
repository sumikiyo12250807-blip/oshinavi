# -*- coding: utf-8 -*-
# 背景の動画 40242 を見る＝1秒ごとのコマを並べた一覧と、上下の明るさ
import glob, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
fs = sorted(glob.glob(D + 'bgpeek/*.png'))
out = Image.new('RGB', (4 * 330, ((len(fs) + 3) // 4) * 190), (0, 0, 0))
for i, f in enumerate(fs):
    im = Image.open(f).convert('RGB')
    a = np.asarray(im).astype(float).mean(axis=2)
    print('%s 全体 %.0f 上1/3 %.0f 中 %.0f 下1/3 %.0f' % (f[-6:-4], a.mean(), a[:120].mean(), a[120:240].mean(), a[240:].mean()))
    out.paste(im.resize((320, 180)), ((i % 4) * 330, (i // 4) * 190))
out.save(D + 'bgpeek/sheet.png')
