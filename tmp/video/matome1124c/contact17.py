# -*- coding: utf-8 -*-
# 場面ごとの静止画（frames/h_*.png）を 7 枚×2 段に並べる → contact17.png（絵コンテのページ用）
import glob, os
from PIL import Image, ImageDraw
import sys
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import oshimade_mv as M
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
fs = sorted(glob.glob(D + 'frames/h_*.png'))
w, h = 300, 533
cols = 7
rows = (len(fs) + cols - 1) // cols
out = Image.new('RGB', (cols * (w + 10) + 10, rows * (h + 50) + 10), (20, 14, 30))
d = ImageDraw.Draw(out)
for i, f in enumerate(fs):
    im = Image.open(f).convert('RGB').resize((w, h), Image.LANCZOS)
    x, y = 10 + (i % cols) * (w + 10), 10 + (i // cols) * (h + 50)
    out.paste(im, (x, y + 40))
    d.text((x + 4, y + 4), os.path.basename(f)[2:-4].lstrip('0') + ' 秒', font=M.font(30), fill=(255, 230, 120))
out.save(D + 'contact17.png')
