# -*- coding: utf-8 -*-
"""「最新のCD」の画像を型にするための下調べ（2026-09-15 夜）。
・画像の大きさ
・白い字の範囲（R,G,B すべて 200 以上）
・CDの絵の範囲（紫〜虹色＝R が G より 40 以上大きい画素）
・字の上下の行で、背景（字のない所）の色を横に何か所か拾う
"""
from PIL import Image

SRC = r"C:\Users\user\Downloads\Gemini_Generated_Image_1jgqey1jgqey1jgq.jpg"
im = Image.open(SRC).convert('RGB')
w, h = im.size
px = im.load()
print('size', w, h)

def bbox(cond, y0=60, y1=490, x0=60, x1=None):
    x1 = x1 or w - 60
    xs, ys = [], []
    for y in range(y0, y1, 2):
        for x in range(x0, x1, 2):
            if cond(px[x, y]):
                xs.append(x); ys.append(y)
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None

white = lambda p: p[0] >= 200 and p[1] >= 200 and p[2] >= 200
purple = lambda p: p[0] - p[1] >= 40 and p[2] >= 120
print('white bbox (text+?)', bbox(white))
print('white bbox left of x=1280', bbox(white, x1=1280))
print('purple bbox', bbox(purple))
for y in (120, 150, 200, 300, 400, 440, 470):
    print('row', y, [px[x, y] for x in (80, 110, 140, 170, 700, 1250, 1290, 1720)])
