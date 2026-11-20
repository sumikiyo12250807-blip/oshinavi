# -*- coding: utf-8 -*-
# frames/h_*.png を縮小して1枚に並べる（下見）
import glob, sys
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
fs = sorted(glob.glob(D + 'frames/h_*.png'))
w, h = 270, 480
cols = 5
rows = (len(fs) + cols - 1) // cols
out = Image.new('RGB', (cols * (w + 8) + 8, rows * (h + 30) + 8), (40, 40, 40))
for i, f in enumerate(fs):
    im = Image.open(f).convert('RGB').resize((w, h))
    x, y = 8 + (i % cols) * (w + 8), 8 + (i // cols) * (h + 30)
    out.paste(im, (x, y + 22))
    ImageDraw.Draw(out).text((x, y + 4), f.split('h_')[-1], fill=(255, 255, 255))
out.save(D + (sys.argv[1] if len(sys.argv) > 1 else 'contact.png'))
print(len(fs))
