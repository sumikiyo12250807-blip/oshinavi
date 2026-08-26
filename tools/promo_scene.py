# -*- coding: utf-8 -*-
"""OSHINAVI宣伝動画のシーン画像を組む（背景＝実サイトの画面／右にお毒姐さん）。

  python tools/promo_scene.py --bg tmp/promo/site_bg.png --char tmp/promo/char.png \
      --out tmp/promo/scene.png --char-h 950

X投稿の朗読動画（tools/x_scene.py）と同じ考え方＝背景は実物の画面をそのまま置き、
H3には「背景は1pxも描き直すな」と言う。ここでは背景がXカードでなく OSHINAVI 本体。
"""
import io, os, sys, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = r"C:\Windows\Fonts\meiryob.ttc"
FONT_REG = r"C:\Windows\Fonts\meiryo.ttc"

W, H = 1080, 1920
NEON = (57, 255, 176)      # サイトの見出しと同じ系統の蛍光グリーン
WHITE = (255, 255, 255)
SUB = (200, 210, 225)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bg", required=True)
    ap.add_argument("--char", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--char-h", type=int, default=950)
    ap.add_argument("--char-x", type=int, default=None, help="左端x(省略時は右寄せ)")
    ap.add_argument("--scrim-top", type=int, default=1180)
    ap.add_argument("--catch", default="推しのチケット、\nぜんぶここ。")
    ap.add_argument("--url", default="oshinavi.jp")
    ap.add_argument("--note", default="発売日カウントダウン／無料")
    ap.add_argument("--text-y", type=int, default=1420)
    a = ap.parse_args()

    bg = Image.open(a.bg).convert("RGBA").resize((W, H))

    # 下半分に黒のグラデを敷いて、文字とキャラの足元を締める
    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    for y in range(a.scrim_top, H):
        t = (y - a.scrim_top) / float(H - a.scrim_top)
        sd.line([(0, y), (W, y)], fill=(3, 6, 14, int(248 * (t ** 0.85))))
    bg = Image.alpha_composite(bg, scrim)

    # キャラ（右寄せ・接地）
    ch = Image.open(a.char).convert("RGBA")
    cw = int(ch.width * a.char_h / ch.height)
    ch = ch.resize((cw, a.char_h), Image.LANCZOS)
    cx = a.char_x if a.char_x is not None else W - cw
    bg.alpha_composite(ch, (cx, H - a.char_h))

    d = ImageDraw.Draw(bg)
    f_catch = ImageFont.truetype(FONT_BOLD, 62)
    f_url = ImageFont.truetype(FONT_BOLD, 76)
    f_note = ImageFont.truetype(FONT_REG, 30)

    x, y = 46, a.text_y
    for line in a.catch.split("\n"):
        # 読みやすさのための縁取り
        d.text((x, y), line, font=f_catch, fill=WHITE,
               stroke_width=6, stroke_fill=(0, 0, 0))
        y += 78
    y += 26
    d.text((x, y), a.url, font=f_url, fill=NEON,
           stroke_width=7, stroke_fill=(0, 0, 0))
    y += 100
    d.text((x, y), a.note, font=f_note, fill=SUB,
           stroke_width=4, stroke_fill=(0, 0, 0))

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    bg.convert("RGB").save(a.out)
    print("シーン画像 → %s  キャラ %dx%d を x=%d に配置" % (a.out, cw, a.char_h, cx))


if __name__ == "__main__":
    main()
