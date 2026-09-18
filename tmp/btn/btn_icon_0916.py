# -*- coding: utf-8 -*-
"""ボタン画像にロゴ（アイコン）を足す（2026-09-16 夜）。

ユーザー「会場近くのホテルを探すでよさそう　ホテルの方が、若い人にはわかりやすいから」
        「ホテルのロゴとチケットぴあにはチケットのロゴ」

・型は tmp/btn/btn_from_cd_0915.py と同じ（「最新のCD」の画像の枠＋字の作り）。
  あの道具は import するとトップレベルで JOBS を全部作ってしまうので、必要な所だけ写している。
・ちがうのはアイコン＝9/15 はユーザーが作った絵から光だけを抜いたが、
  ホテルとチケットの絵は手元に無いので **線画をこの中で描く**（水色→白のネオン＋外側の光）。
使い方: python tmp/btn/btn_icon_0916.py [hotel] [pia]   （名前を省くと両方）
出力は tmp/btn_tpl/（*_full.png と *_88.png）
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

DL = r"C:\Users\user\Downloads"
CD = os.path.join(DL, "Gemini_Generated_Image_1jgqey1jgqey1jgq.jpg")
FONT = r"C:\Windows\Fonts\NotoSansJP-VF.ttf"
FONT_FALLBACK = r"C:\Windows\Fonts\HGSoeiKakugothicUB_X0213(04).ttc"
OUTDIR = "tmp/btn_tpl"
FRAME_T, FRAME_B = 52, 496
CAPW = 230
TEXT_X, GAP, RIGHT_PAD = 172, 40, 156
INK_H = 238
MID_Y = 275
EXTRUDE = 16

CYAN = (40, 150, 255)
WHITE = (255, 255, 255)


def load(path):
    return np.asarray(Image.open(path).convert('RGB')).astype(np.float32)


def blur(a, r):
    return np.asarray(Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255


def dilate(a, size):
    return np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(size))).astype(np.float32) / 255


src = load(CD)
H, W, _ = src.shape

white = ((src[..., 0] > 150) & (src[..., 1] > 150) & (src[..., 2] > 150)).astype(np.float32)
white[:, 1240:] = 0
fg = dilate(white, 51)
fg_soft = np.clip(blur(fg, 10) * 1.3, 0, 1)

prof = np.full((H, 3), np.nan, np.float32)
mx = src.max(axis=2)
for y in range(H):
    if y < 100 or y > 468:
        prof[y] = np.median(src[y, 300:1100], axis=0)
        continue
    ok = (fg[y, 200:1240] == 0) & (mx[y, 200:1240] < 100)
    if ok.sum() >= 20:
        prof[y] = np.median(src[y, 200:1240][ok], axis=0)
ys = np.arange(H)
for c in range(3):
    good = ~np.isnan(prof[:, c])
    prof[:, c] = np.interp(ys, ys[good], prof[good, c])
k = np.exp(-0.5 * (np.arange(-9, 10) / 3.0) ** 2); k /= k.sum()
for c in range(3):
    sm = np.convolve(np.pad(prof[:, c], 9, mode='edge'), k, mode='valid')
    prof[100:469, c] = sm[100:469]

ramp = np.clip((CAPW - np.arange(CAPW)) / 40.0, 0, 1)[None, :]
A = ((1 - fg_soft[:, :CAPW]) * ramp)[..., None]
capL = src[:, :CAPW] * A + prof[:, None, :] * (1 - A)


def make_template(Wn):
    rng = np.random.default_rng(0)
    T = np.repeat(prof[:, None, :], Wn, axis=1) + rng.normal(0, 1.2, (H, Wn, 1))
    T[:, :CAPW] = capL
    T[:, Wn - CAPW:] = capL[:, ::-1]
    return T


def get_font(size):
    try:
        f = ImageFont.truetype(FONT, size)
        f.set_variation_by_axes([900])
        return f, 'NotoSansJP 900'
    except Exception:
        return ImageFont.truetype(FONT_FALLBACK, size), 'HG創英角ゴシックUB'


f100, fname = get_font(100)
b = f100.getbbox("最")
SIZE = round(100 * INK_H / (b[3] - b[1]))
font, fname = get_font(SIZE)
rb = font.getbbox("最")
Y_OFF = MID_Y - (rb[1] + rb[3]) / 2
INK_T, INK_B = Y_OFF + rb[1], Y_OFF + rb[3]


def text_masks(text, Wn, x):
    def draw(stroke):
        im = Image.new('L', (Wn, H), 0)
        ImageDraw.Draw(im).text((x, Y_OFF), text, font=font, fill=255, stroke_width=stroke, stroke_fill=255)
        return np.asarray(im).astype(np.float32) / 255
    return draw(0), draw(5)


def shift(a, dx, dy):
    out = np.zeros_like(a)
    out[dy:, dx:] = a[:a.shape[0] - dy, :a.shape[1] - dx]
    return out


def vgrad(c_top, c_bot, t, b):
    y = np.clip((np.arange(H) - t) / max(1, b - t), 0, 1)[:, None, None]
    return np.array(c_top, np.float32) * (1 - y) + np.array(c_bot, np.float32) * y


# ---------------- ここからが新しい所＝ロゴを線で描く ----------------
# 大きめ（S=4倍）に描いてから縮める＝線のふちがなめらかになる
S = 4
ICON_H = 300          # ボタンの中でのアイコンの高さ（字 238px より少し大きい）
LW = 15               # 線の太さ（縮める前）


def draw_hotel(d, w, h):
    """ホテル＝建物＋窓＋入口＋上の看板の光。若い人にも「宿」と分かる形にする。"""
    lw = LW
    x0, x1 = int(w * 0.14), int(w * 0.86)
    y0, y1 = int(h * 0.26), int(h * 0.94)
    # 建物の外枠
    d.rectangle([x0, y0, x1, y1], outline=255, width=lw)
    # 屋根の上の看板（横線＋短い支柱）
    sy = int(h * 0.10)
    d.rectangle([int(w * 0.30), sy, int(w * 0.70), int(h * 0.19)], outline=255, width=lw)
    d.line([int(w * 0.50), int(h * 0.19), int(w * 0.50), y0], fill=255, width=lw)
    # 窓（2列×2段・88pxに縮めてもつぶれない大きさにする）
    cols = [int(w * 0.25), int(w * 0.54)]
    ww, wh = int(w * 0.21), int(h * 0.15)
    for r in range(2):
        wy = y0 + int(h * 0.11) + r * int(h * 0.22)
        for cx in cols:
            d.rectangle([cx, wy, cx + ww, wy + wh], outline=255, width=lw)
    # 入口（下の真ん中）
    dw = int(w * 0.20)
    dx = int(w * 0.50) - dw // 2
    d.rectangle([dx, y1 - int(h * 0.17), dx + dw, y1], outline=255, width=lw)


def draw_ticket(d, w, h):
    """チケット＝もぎる半券。上下から丸く食い込ませて「切り込み」を作り、右側を点線で区切る。

    はじめ弧を線で足したら、四角の外に輪が飛び出して半券に見えなかった（9/16 夜に作り直し）。
    切り込みは**線を消して**作る＝輪郭を描いたあと、その位置に黒い丸を塗って食い込ませる。
    """
    lw = LW
    x0, x1 = int(w * 0.07), int(w * 0.93)
    y0, y1 = int(h * 0.26), int(h * 0.80)
    d.rounded_rectangle([x0, y0, x1, y1], radius=int(h * 0.09), outline=255, width=lw)
    # 券面の文字を表す2本の線（左の広い方）
    d.line([int(w * 0.15), int(h * 0.42), int(w * 0.52), int(h * 0.42)], fill=255, width=lw)
    d.line([int(w * 0.15), int(h * 0.58), int(w * 0.44), int(h * 0.58)], fill=255, width=lw)
    # もぎり線（縦の点線）＝右から4分の1くらいの所
    cx = int(w * 0.68)
    r = int(h * 0.10)
    yy = y0 + r
    step = int(h * 0.11)
    while yy < y1 - r:
        d.line([cx, yy, cx, min(yy + int(h * 0.055), y1 - r)], fill=255, width=max(5, lw - 4))
        yy += step
    # 切り込み＝上下の輪郭を丸く食い込ませる（黒で塗って線を消す）
    d.ellipse([cx - r, y0 - r, cx + r, y0 + r], fill=0)
    d.ellipse([cx - r, y1 - r, cx + r, y1 + r], fill=0)
    # 食い込みのふち＝残っている半円だけを描き直す（内側に向いた弧）
    d.arc([cx - r, y0 - r, cx + r, y0 + r], start=0, end=180, fill=255, width=lw)
    d.arc([cx - r, y1 - r, cx + r, y1 + r], start=180, end=360, fill=255, width=lw)
    # 右の小片に「座席の丸」を1つ
    d.ellipse([int(w * 0.78), int(h * 0.45), int(w * 0.86), int(h * 0.57)], outline=255, width=lw)


def make_icon(kind):
    """線画を描いて、CDの型と同じ『水色→白のネオン＋外の光』のRGBAにする。"""
    w, h = (int(ICON_H * 0.92) * S, ICON_H * S) if kind == 'hotel' else (int(ICON_H * 1.25) * S, ICON_H * S)
    im = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(im)
    if kind == 'hotel':
        draw_hotel(d, w, h)
    else:
        draw_ticket(d, w, h)
    im = im.resize((w // S, h // S), Image.LANCZOS)
    core = np.asarray(im).astype(np.float32) / 255            # 線の芯
    glow = np.clip(blur(dilate(core, 9), 7) * 1.6, 0, 1)      # まわりの光
    # 色＝芯は白、まわりは水色（CDのアイコンと同じ配色）
    color = np.array(CYAN, np.float32)[None, None, :] * (1 - core[..., None]) \
        + np.array(WHITE, np.float32)[None, None, :] * core[..., None]
    alpha = np.clip(core + glow * 0.75, 0, 1)
    rgba = np.dstack([color, alpha[..., None] * 255])
    s = (FRAME_B - FRAME_T) / (FRAME_B - FRAME_T)             # 既に狙いの高さで描いている
    out = Image.fromarray(np.clip(rgba, 0, 255).astype(np.uint8), 'RGBA')
    if s != 1:
        out = out.resize((round(out.width * s), round(out.height * s)), Image.LANCZOS)
    return np.asarray(out).astype(np.float32)


JOBS = {
    'hotel': ('hotel_logo', '会場近くのホテルを探す', 'hotel'),
    'pia': ('pia_logo', 'チケットぴあ', 'ticket'),
    # 🆕2026-09-18 ユーザー「**楽天チケットのボタンもローチケのもそろえて作らないとだね**」
    #   ＝ぴあだけ画像で、他の売り場は字＋絵文字のままだったので、同じ型でそろえた。
    #   ⚠️各社のロゴは手元に無いし勝手に使えないので、**ぴあと同じ「もぎる半券」の線画**で統一する
    #   （ブランドのロゴを真似て描くのはやらない）。
    'rakuten': ('rakuten_logo', '楽天チケット', 'ticket'),
    'lawson': ('lawson_logo', 'ローソンチケット', 'ticket'),
    'eplus': ('eplus_logo', 'e+', 'ticket'),
    'tiget': ('tiget_logo', 'TIGET', 'ticket'),
}


def build(name, text, kind):
    tb = font.getbbox(text)
    tw = tb[2] - tb[0]
    icon = make_icon(kind)
    Wn = TEXT_X + tw + GAP + icon.shape[1] + RIGHT_PAD
    T = make_template(Wn)
    M, Ms = text_masks(text, Wn, TEXT_X - tb[0])
    E = np.zeros_like(Ms)
    for dd in range(1, EXTRUDE + 1):
        E = np.maximum(E, shift(Ms, round(dd * 0.2), dd))
    G = blur(np.maximum(Ms, E), 22)
    glow = np.array((30, 110, 255), np.float32)
    T = 255 - (255 - T) * (1 - (glow / 255) * (0.8 * G)[..., None])
    ext = vgrad((50, 120, 255), (12, 40, 170), INK_T, INK_B + EXTRUDE)
    T = T * (1 - E[..., None]) + ext * E[..., None]
    T = T * (1 - Ms[..., None]) + np.array((185, 230, 255), np.float32) * Ms[..., None]
    fill = vgrad((255, 255, 255), (190, 230, 248), INK_T, INK_B)
    T = T * (1 - M[..., None]) + fill * M[..., None]
    ih, iw = icon.shape[:2]
    ix = TEXT_X + tw + GAP
    iy = round(MID_Y - ih / 2)
    a = icon[..., 3:4] / 255
    T[iy:iy + ih, ix:ix + iw] = T[iy:iy + ih, ix:ix + iw] * (1 - a) + icon[..., :3] * a
    out = Image.fromarray(np.clip(T, 0, 255).astype(np.uint8))
    full = out.crop((0, FRAME_T - 12, Wn, FRAME_B + 13))
    os.makedirs(OUTDIR, exist_ok=True)
    full.save(os.path.join(OUTDIR, name + '_full.png'))
    small = full.resize((round(full.width * 88 / full.height), 88), Image.LANCZOS)
    small.save(os.path.join(OUTDIR, name + '_88.png'), optimize=True)
    print('%s ｜%s ｜%dx88 ｜%dKB' % (name, text, small.width, os.path.getsize(os.path.join(OUTDIR, name + '_88.png')) // 1024))
    return full


want = [a for a in sys.argv[1:] if a in JOBS] or list(JOBS)
fulls = [build(*JOBS[k]) for k in want]

# 見比べ＝上に元の「最新のCD」、下に作ったもの
ref = Image.open(CD).convert('RGB').crop((0, FRAME_T - 12, W, FRAME_B + 13))
rows = [ref] + fulls
rows = [r.resize((round(r.width * 120 / r.height), 120), Image.LANCZOS) for r in rows]
sheet = Image.new('RGB', (max(r.width for r in rows) + 40, sum(r.height + 20 for r in rows) + 20), (14, 14, 22))
y = 20
for r in rows:
    sheet.paste(r, (20, y)); y += r.height + 20
sheet.save(os.path.join(OUTDIR, 'sheet_logo_0916.png'))
print('sheet', sheet.size)
