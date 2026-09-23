# -*- coding: utf-8 -*-
"""参照画像に置く木の椅子（背もたれ付き・斜め45度くらい）を描いて RGBA で返す（2026-09-24）。
H3 は参照画像にあるものを使う＝椅子は言葉でなく絵で渡す（[[project_odoku_x_video]] の教訓）。"""
from PIL import Image, ImageDraw, ImageFilter

WOOD = (132, 84, 48)
WOOD_D = (92, 56, 30)
WOOD_L = (168, 112, 66)


def chair(h=560):
    s = h / 560
    W, H = int(380 * s), h
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    P = lambda *xy: [(int(x * s), int(y * s)) for x, y in xy]
    # 奥の脚
    d.polygon(P((250, 330), (266, 330), (262, 548), (248, 548)), fill=WOOD_D)
    d.polygon(P((82, 312), (98, 312), (96, 520), (82, 520)), fill=WOOD_D)
    # 背もたれ（2本の柱＋横木3本）
    d.polygon(P((72, 20), (96, 16), (100, 318), (78, 322)), fill=WOOD)
    d.polygon(P((236, 36), (258, 32), (262, 322), (240, 326)), fill=WOOD)
    for y in (40, 110, 180):
        d.polygon(P((90, y), (246, y + 14), (246, y + 44), (90, y + 30)), fill=WOOD_L)
        d.line(P((90, y + 30), (246, y + 44)), fill=WOOD_D, width=max(1, int(3 * s)))
    # 座面（奥行きのある台形＋厚み）
    d.polygon(P((70, 300), (270, 316), (350, 380), (120, 368)), fill=WOOD_L)
    d.polygon(P((120, 368), (350, 380), (350, 402), (120, 390)), fill=WOOD_D)
    d.polygon(P((70, 300), (120, 368), (120, 390), (70, 322)), fill=WOOD)
    # 手前の脚
    d.polygon(P((122, 388), (140, 388), (138, 556), (122, 556)), fill=WOOD)
    d.polygon(P((330, 398), (348, 398), (344, 560), (328, 560)), fill=WOOD)
    # 貫（脚をつなぐ棒）
    d.polygon(P((130, 470), (338, 480), (338, 490), (130, 480)), fill=WOOD_D)
    return im.filter(ImageFilter.SMOOTH)
