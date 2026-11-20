# -*- coding: utf-8 -*-
# 撮ったタップの画面に、測った箱をピンクで描いて縮めて見る
import io, json
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/cards/'
im = Image.open(D + 'screen_badge.png').convert('RGB')
bx = json.load(io.open(D + 'screen_badge.json'))['boxes']
d = ImageDraw.Draw(im)
for b in bx:
    d.rectangle(b, outline=(255, 60, 160), width=10)
im.resize((540, 960)).save(D + 'look_badge.png')
