# -*- coding: utf-8 -*-
"""X投稿に添える宣材画像を組む（恒久ツール・2026-08-30 新設）。

OSHINAVI のカード表示を撮ったスクショを受け取り、
上に「OSHINAVI／推しのチケット発売日」、下に「oshinavi.jp／発売日カウントダウン・無料」を載せる。

🚨 `oshinavi.jp` の文字は **緑にしない。白＋発光**（memory: feedback_x_image_url_white_glow）。
   ユーザー「緑は嫌だ」（2026-08-29）。2026-08-29 に使った (0,255,170) は不採用。

使い方:
  python tools/x_promo_image.py --src tmp/promo/card_xxx.png --out tmp/promo/x1_xxx.jpg
  python tools/x_promo_image.py --src ... --out ... --crop 0,300,1366,1000   # 中身だけ切る
"""
import argparse
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

FONT_BOLD = r"C:\Windows\Fonts\meiryob.ttc"
FONT_REG = r"C:\Windows\Fonts\meiryo.ttc"

BG = (10, 8, 20)              # サイトの地に寄せた濃紺
PURPLE = (190, 150, 255)      # サイトの見出し色（緑は使わない）
WHITE = (255, 255, 255)
GRAY = (200, 200, 210)

TOP_H = 96                    # 上の帯
BOTTOM_H = 132                # 下の帯


def glow_text(im, xy, text, font, fill=WHITE):
    """白文字を発光させて置く。

    ぼかし半径を変えた層を2枚重ねる＝広いにじみ（外側の光）＋狭いにじみ（芯の明るさ）。
    1層だけだと下の影に負けて「ただの白文字」に見える（2026-08-30 に実際そうなった）。
    """
    for radius, stroke, strength in ((18, 4, 0.55), (7, 0, 0.5)):
        glow = Image.new("RGB", im.size, (0, 0, 0))
        ImageDraw.Draw(glow).text(xy, text, font=font, fill=fill,
                                  stroke_width=stroke, stroke_fill=fill)
        glow = glow.filter(ImageFilter.GaussianBlur(radius))
        glow = glow.point(lambda v: int(v * strength))   # 強すぎると白飛びして字が読めない
        im = ImageChops.add(im, glow)
    d = ImageDraw.Draw(im)
    d.text((xy[0] + 2, xy[1] + 2), text, font=font, fill=(20, 10, 40))  # 影は薄く＝光を消さない
    d.text(xy, text, font=font, fill=fill)
    return im


def build(src, out, crop=None, headline="推しのチケット発売日", tagline="発売日カウントダウン／無料"):
    base = Image.open(src).convert("RGB")
    if crop:
        base = base.crop(crop)
    w = base.width
    canvas = Image.new("RGB", (w, base.height + TOP_H + BOTTOM_H), BG)
    canvas.paste(base, (0, TOP_H))
    d = ImageDraw.Draw(canvas)

    f_logo = ImageFont.truetype(FONT_BOLD, 44)
    f_head = ImageFont.truetype(FONT_REG, 27)
    f_url = ImageFont.truetype(FONT_BOLD, 62)
    f_tag = ImageFont.truetype(FONT_REG, 27)

    # 上の帯＝OSHINAVI（紫）＋ 見出し（白）
    d.text((40, TOP_H // 2 - 26), "OSHINAVI", font=f_logo, fill=PURPLE)
    x = 40 + d.textlength("OSHINAVI", font=f_logo) + 22
    d.text((x, TOP_H // 2 - 14), headline, font=f_head, fill=GRAY)

    # 下の帯＝oshinavi.jp（🚨白＋発光）＋ 添え文（白）
    uy = TOP_H + base.height + 22
    canvas = glow_text(canvas, (40, uy), "oshinavi.jp", font=f_url)
    d = ImageDraw.Draw(canvas)
    ux = 40 + d.textlength("oshinavi.jp", font=f_url) + 28
    d.text((ux, uy + 26), tagline, font=f_tag, fill=GRAY)

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    canvas.convert("RGB").save(out, quality=92)
    print("wrote %s (%dx%d)" % (out, canvas.width, canvas.height))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--crop", default="", help="left,top,right,bottom")
    ap.add_argument("--headline", default="推しのチケット発売日")
    ap.add_argument("--tagline", default="発売日カウントダウン／無料")
    a = ap.parse_args()
    crop = tuple(int(x) for x in a.crop.split(",")) if a.crop else None
    build(a.src, a.out, crop, a.headline, a.tagline)


if __name__ == "__main__":
    main()
