# -*- coding: utf-8 -*-
"""X投稿の見た目を1080x1920の画像に組む（動画の背景に使う）。

ユーザー案（2026-08-02）＝「背景＝X投稿をくっきり見せる／お毒姐さんは小さめで解説役」。
実投稿のスクショはまだ無いので、投稿本文から見た目を組み立てる。

使い方:
  python tools/x_card_image.py --text tmp/xpost_0805_necry.txt --out tmp/video/bg_0805.png
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920

BG = (0, 0, 0)
FG = (231, 233, 234)          # Xの本文色
SUB = (113, 118, 123)         # @IDやタイムスタンプ
LINK = (29, 155, 240)         # リンクの青
CARD_X = 56

FONT_BOLD = r"C:\Windows\Fonts\meiryob.ttc"
FONT_REG = r"C:\Windows\Fonts\meiryo.ttc"


FONT_EMOJI = r"C:\Windows\Fonts\seguiemj.ttf"


def _today_stamp():
    """Xの投稿の末尾に出る日時表記を今日の日付で作る（2026-08-05 追加・以前は8/4固定だった）。"""
    import datetime
    n = datetime.datetime.now()
    ap_ = "午前" if n.hour < 12 else "午後"
    h = n.hour % 12 or 12
    return "%s%d:%02d · %d年%d月%d日" % (ap_, h, n.minute, n.year, n.month, n.day)


def is_emoji(ch):
    o = ord(ch)
    return (0x1F300 <= o <= 0x1FAFF) or (0x2600 <= o <= 0x27BF) or o == 0xFE0F


def char_w(draw, ch, font, femoji):
    return draw.textlength(ch, font=femoji if (femoji and is_emoji(ch)) else font)


def draw_mixed(draw, xy, text, font, femoji, fill):
    """メイリオに絵文字が無いので、絵文字だけ Segoe UI Emoji で描く。"""
    x, y = xy
    for ch in text:
        if femoji and is_emoji(ch):
            try:
                draw.text((x, y), ch, font=femoji, embedded_color=True)
            except TypeError:
                draw.text((x, y), ch, font=femoji, fill=fill)
            x += draw.textlength(ch, font=femoji)
        else:
            draw.text((x, y), ch, font=font, fill=fill)
            x += draw.textlength(ch, font=font)


def wrap(draw, text, font, max_w, femoji=None):
    lines = []
    for para in text.split("\n"):
        if not para:
            lines.append("")
            continue
        cur, wsum = "", 0.0
        for ch in para:
            cw = char_w(draw, ch, font, femoji)
            if wsum + cw > max_w and cur:
                lines.append(cur)
                cur, wsum = ch, cw
            else:
                cur += ch
                wsum += cw
        lines.append(cur)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--out", default=os.path.join(REPO, "tmp", "video", "bg.png"))
    ap.add_argument("--size", type=int, default=36, help="本文の文字サイズ")
    ap.add_argument("--stamp", default="", help='末尾の日時（例 "午後8:00 · 2026年8月5日"）。空なら今日')
    args = ap.parse_args()

    with open(args.text, encoding="utf-8-sig") as f:
        body = f.read().rstrip("\n")

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    f_name = ImageFont.truetype(FONT_BOLD, 38)
    f_id = ImageFont.truetype(FONT_REG, 32)
    f_body = ImageFont.truetype(FONT_REG, args.size)
    f_meta = ImageFont.truetype(FONT_REG, 30)

    # アイコン（サイトのlogo.pngを丸く切る）
    y = 150
    logo_path = os.path.join(REPO, "logo.png")
    icon_d = 84
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGB").resize((icon_d, icon_d))
        mask = Image.new("L", (icon_d, icon_d), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, icon_d, icon_d], fill=255)
        img.paste(logo, (CARD_X, y), mask)
    else:
        d.ellipse([CARD_X, y, CARD_X + icon_d, y + icon_d], fill=(29, 155, 240))

    d.text((CARD_X + icon_d + 22, y + 6), "OSHINAVI", font=f_name, fill=FG)
    d.text((CARD_X + icon_d + 22, y + 50), "@oshinavinavi", font=f_id, fill=SUB)

    # 本文
    y += icon_d + 40
    max_w = W - CARD_X * 2
    lh = int(args.size * 1.75)
    f_emoji = ImageFont.truetype(FONT_EMOJI, args.size) if os.path.exists(FONT_EMOJI) else None
    for ln in wrap(d, body, f_body, max_w, f_emoji):
        if not ln:
            y += int(lh * 0.5)
            continue
        color = LINK if ln.startswith("https://") or ln.startswith("#") else FG
        draw_mixed(d, (CARD_X, y), ln, f_body, f_emoji, color)
        y += lh

    # 下の余白にタイムスタンプ風の一行（Xらしさ）
    y += 20
    stamp = args.stamp or _today_stamp()
    d.text((CARD_X, y), stamp, font=f_meta, fill=SUB)
    y += 56
    d.line([CARD_X, y, W - CARD_X, y], fill=(47, 51, 54), width=2)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    img.save(args.out)
    print("%s  本文の下端 y=%d / 高さ%d" % (args.out, y, H))


main()
