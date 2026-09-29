# -*- coding: utf-8 -*-
"""『Mamma Mia Midnight』用の参照画像（課金前の絵コンテ）＝真夜中のネオン街＋OSHINAVIのネオン看板＋お毒姐さん。
  python tools/mamma_ref.py --char <切り抜きPNG> --out <png> [--char-h 1100]"""
import argparse, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W, H = 1080, 1920
ap = argparse.ArgumentParser()
ap.add_argument('--char', default='tmp/video/flash_0924/char_cut.png')
ap.add_argument('--out', default='tmp/video/mamma/ref.png')
ap.add_argument('--char-h', type=int, default=1100)
a = ap.parse_args()
im = Image.new('RGB', (W, H))
d = ImageDraw.Draw(im)
for y in range(H):                                   # 真夜中の空：濃紺→紫
    k = y / H
    d.line([0, y, W, y], fill=(int(12 + 40 * k), int(6 + 10 * k), int(40 + 50 * k)))
rnd = random.Random(4)
glow = Image.new('RGB', (W, H))
g = ImageDraw.Draw(glow)
for _ in range(60):                                  # 街の灯のボケ
    x, y, r = rnd.randrange(W), rnd.randrange(700, 1500), rnd.randrange(18, 60)
    c = rnd.choice([(255, 80, 200), (34, 230, 245), (255, 214, 102), (170, 120, 255)])
    g.ellipse([x - r, y - r, x + r, y + r], fill=c)
glow = glow.filter(ImageFilter.GaussianBlur(22))
im = Image.blend(im, glow, 0.45)
d = ImageDraw.Draw(im)
f = ImageFont.truetype(r'C:\Windows\Fonts\YuGothB.ttc', 150)
lay = Image.new('RGB', (W, H))                        # ネオン看板 OSHINAVI
ImageDraw.Draw(lay).text((W / 2, 300), 'OSHINAVI', font=f, fill=(255, 80, 200), anchor='mm', stroke_width=10, stroke_fill=(255, 80, 200))
lay = lay.filter(ImageFilter.GaussianBlur(20))
im = Image.blend(im, Image.eval(lay, lambda v: v), 0.0)
im.paste(lay, (0, 0), lay.convert('L'))
ImageDraw.Draw(im).text((W / 2, 300), 'OSHINAVI', font=f, fill=(255, 235, 250), anchor='mm')
ImageDraw.Draw(im).rectangle([0, 1700, W, H], fill=(20, 10, 36))   # 床
c = Image.open(a.char).convert('RGBA')
r = a.char_h / c.height
c = c.resize((int(c.width * r), a.char_h), Image.LANCZOS)
im.paste(c, (W // 2 - c.width // 2, 1760 - a.char_h), c)
im.save(a.out)
print(a.out, 'キャラ高さ %dpx（画面の%d%%）' % (a.char_h, round(100 * a.char_h / H)))
