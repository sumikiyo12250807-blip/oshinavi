# -*- coding: utf-8 -*-
# 「発売日のバッジをタップ」の場面（matome1024j/badge_tap.py の写し）＝10/27発売の 神田伯山一門会（28404）のカード（screen_badge.png＝shoot_badge.py）
#   画面いっぱい本物のOSHINAVI（スマホ幅）・押している箱全体をピンクの太い角丸の枠＋光・歌詞は下の暗い帯
#   今回はキャラを切り抜いて貼らない（DJの絵はコマの場面だけ）＝キャラの paste は無し
from PIL import Image, ImageDraw, ImageFilter
import oshimade_mv as M

PINK = (224, 64, 251)
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/cards/'
IMG = D + 'screen_badge.png'
import json as _j
BOXES = _j.load(open(D + 'screen_badge.json'))['boxes'][:1] or [[78, 617, 1036, 852]]   # 11/9 測った箱   # 11/6：41806 又吉直樹一人コントライブ「人間」「一般発売（東京 12/12公演）11/6 10:00 明日発売」の箱（shoot_badge が測った）
RAD = 34
BAND = (0, 1400, 1080, 1920)   # 11/13 とろサーモン久保田のカードは受付が3つ＝タップの箱が下（〜1366）まで来る＝帯を 1300→1400 に下げて「発売開始まであと3日」に重ねない


def install(render_fn):
    G = render_fn.__globals__
    orig_scene = G['shot_scene']
    _scr = {}

    def screen():
        if 'im' not in _scr:
            _scr['im'] = Image.open(IMG).convert('RGB')
        return _scr['im']

    def shot_scene(im, key, t, u, L, S):
        if key != 'badge':
            return orig_scene(im, key, t, u, L, S)
        W = M.W
        a = M.ease(u / 0.45)
        x0 = int((1 - a) * W)
        im.paste(screen(), (x0, 0))
        band = Image.new('RGBA', (BAND[2] - BAND[0], BAND[3] - BAND[1]), (6, 4, 16, 205))
        im.paste(band, (BAND[0] + x0, BAND[1]), band)
        M.glow_text(im, (W / 2 + x0, BAND[1] + 42), '発売日のバッジをタップ', G['fit']('発売日のバッジをタップ', 64, 900), grad=(M.GOLD, M.PINK), glow=M.PINK)
        boxes = [(b[0] + x0, b[1], b[2] + x0, b[3]) for b in BOXES]
        if u < 0.45:
            return
        span = max(1.0, L)
        cur = min(len(boxes) - 1, int(u / (span / len(boxes))))
        bx0, by0, bx1, by1 = boxes[cur]
        lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).rounded_rectangle([bx0 - 2, by0 - 2, bx1 + 2, by1 + 2], RAD, outline=PINK + (210,), width=14)
        lg = lay.filter(ImageFilter.GaussianBlur(10))
        im.paste(lg, (0, 0), lg)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([bx0, by0, bx1, by1], RAD, outline=PINK, width=7)
        k = (u % (span / len(boxes))) / (span / len(boxes))
        tx, ty = bx0 + 520, by0 + 130
        for j in range(2):
            rr = 16 + 52 * ((k * 2 + j * 0.5) % 1.0)
            al = 1 - ((k * 2 + j * 0.5) % 1.0)
            d.ellipse([tx - rr, ty - rr, tx + rr, ty + rr], outline=tuple(int(v * al) for v in M.WHITE), width=6)
        d.ellipse([tx - 13, ty - 13, tx + 13, ty + 13], fill=M.WHITE)

    G['shot_scene'] = shot_scene
    return G['render']
