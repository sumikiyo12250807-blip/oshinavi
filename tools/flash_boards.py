# -*- coding: utf-8 -*-
"""フラッシュダンス風動画の「流れ」を4コマの絵コンテにする（2026-09-24・課金なし）。
参照画像の背景と切り抜いたキャラを使って、各コマの位置・椅子・水しぶきを簡単に描く。
  python tools/flash_boards.py --dir tmp/video/flash_0924
"""
import argparse
import os
import random
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

FONT = r'C:\Windows\Fonts\meiryob.ttc'


def place(bg, ch, h, cx, bottom, angle=0, flip=False):
    c = ch.resize((int(ch.width * h / ch.height), h), Image.LANCZOS)
    if flip:
        c = c.transpose(Image.FLIP_LEFT_RIGHT)
    if angle:
        c = c.rotate(angle, expand=True, resample=Image.BICUBIC)
    bg.paste(c, (int(cx - c.width / 2), int(bottom - c.height)), c)


def chair(d, cx, bottom, w=300):
    col = (150, 100, 60)
    seat = bottom - 250
    d.rectangle([cx - w // 2, seat, cx + w // 2, seat + 26], fill=col)
    for x in (cx - w // 2 + 10, cx + w // 2 - 30):
        d.rectangle([x, seat + 26, x + 20, bottom], fill=col)
    d.rectangle([cx - w // 2 + 10, seat - 330, cx - w // 2 + 34, seat], fill=col)


def water(img, cx, top, bottom, n=260):
    ov = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    rnd = random.Random(7)
    for _ in range(n):
        x = cx + rnd.gauss(0, 120)
        y = rnd.uniform(top, bottom)
        L = rnd.uniform(30, 110)
        d.line([x, y, x + rnd.uniform(-8, 8), y + L], fill=(190, 230, 255, 200), width=rnd.choice((3, 4, 6)))
    for _ in range(120):
        x, y, r = cx + rnd.gauss(0, 200), bottom - rnd.uniform(0, 300), rnd.uniform(4, 12)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 245, 255, 220))
    img.alpha_composite(ov)


def backlight(img, cx):
    ov = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.polygon([(cx - 60, 0), (cx + 60, 0), (cx + 420, img.height), (cx - 420, img.height)], fill=(255, 250, 220, 70))
    img.alpha_composite(ov)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', required=True)
    ap.add_argument('--char-h', type=int, default=640)
    a = ap.parse_args()
    bg0 = ImageEnhance.Brightness(Image.open(os.path.join(a.dir, 'bg_site.png')).convert('RGB')).enhance(0.72)
    ch = Image.open(os.path.join(a.dir, 'char_cut.png')).convert('RGBA')
    W, H = bg0.size
    B = H - 60
    from draw_chair import chair as chair_img
    cimg = chair_img(int(a.char_h * 0.62))

    def with_chair():
        f = bg0.convert('RGBA')
        f.paste(cimg, ((W - cimg.width) // 2, B - cimg.height), cimg)
        return f
    cx_r = W // 2 + cimg.width // 2 - 40 + int(ch.width * a.char_h / ch.height) // 2
    cuts = []
    # ① 0〜3秒 出だし＝参照画像のまま（椅子は真ん中・キャラは右に立つ）
    f = with_chair(); place(f, ch, a.char_h, cx_r, B); cuts.append((f, '① 0〜3秒', '真ん中に椅子。横に立ってリズムに乗る'))
    # ② 3〜7秒 椅子のまわりを踊る
    f = with_chair(); place(f, ch, a.char_h, W * 0.22, B, angle=8); place(f, ch, a.char_h, W * 0.8, B, angle=-10, flip=True)
    cuts.append((f, '② 3〜7秒', '椅子のまわりで80年代ジャズダンス（回る・キック・髪を振る）'))
    # ③ 7〜10秒 椅子に座って踊る
    f = with_chair(); place(f, ch, int(a.char_h * 0.86), W / 2 + 20, B - 60, angle=-6)
    cuts.append((f, '③ 7〜10秒', '椅子に座る→脚を振り上げ・肩と腕で踊る'))
    # ④ 10〜13秒 のけぞる→上から水
    f = with_chair(); backlight(f, W / 2); place(f, ch, int(a.char_h * 0.86), W / 2 + 20, B - 60, angle=22); water(f, W / 2, 0, B)
    cuts.append((f, '④ 10〜13秒', '座ったままのけぞる→逆光の中、上から水がザーッ'))
    # ⑤ 13〜15秒 決めポーズ
    f = with_chair(); backlight(f, W / 2); place(f, ch, a.char_h, cx_r, B)
    water(f, W / 2, B - 250, B, n=60)
    cuts.append((f, '⑤ 13〜15秒', '立ち上がって決めポーズ（しぶきが光る）'))

    tw, th = W // 2, H // 2
    sheet = Image.new('RGB', (tw * len(cuts) + 10 * (len(cuts) + 1), th + 190), (24, 24, 30))
    dr = ImageDraw.Draw(sheet)
    f1, f2 = ImageFont.truetype(FONT, 40), ImageFont.truetype(FONT, 25)
    for i, (img, t1, t2) in enumerate(cuts):
        x = 10 + i * (tw + 10)
        sheet.paste(img.convert('RGB').resize((tw, th), Image.LANCZOS), (x, 10))
        dr.text((x + 6, th + 25), t1, font=f1, fill=(255, 210, 90))
        # 説明は2行に折る
        lines, cur = [], ''
        for chh in t2:
            if dr.textlength(cur + chh, font=f2) > tw - 12:
                lines.append(cur); cur = ''
            cur += chh
        lines.append(cur)
        for j, ln in enumerate(lines):
            dr.text((x + 6, th + 80 + j * 34), ln, font=f2, fill=(235, 235, 235))
    out = os.path.join(a.dir, 'storyboard_4.png')
    sheet.save(out)
    print(out, sheet.size)


if __name__ == '__main__':
    main()
