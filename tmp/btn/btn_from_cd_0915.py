# -*- coding: utf-8 -*-
"""「最新のCD」の画像を型にして、字とアイコンだけを差し替えたボタン画像を作る（2026-09-15 夜）。
ユーザー「最新のCDが一番しっくり来てて、こんな風に全部をそろえたい／字だけあなたが変えることはできないの？」→見本を見て「いいわ　全部作って」
・型＝CDの画像の左の端（枠・斜めの線）＋それを左右反転した右の端。真ん中は行ごとの背景色で作り直す（字とCDの絵が消える）
・字＝Noto Sans JP の一番太い字（900）＋白→水色のグラデーション＋下へ伸びる青い立体＋青い光
・アイコン＝ユーザーが作った元の画像から、光っている線だけを移す
  （元の背景を引き算する＝ChatGPTの画像は背景の青が明るく、そのまま重ねると四角い箱が見えた／
   探す枠の端にくっついている塊は捨てる＝元の字の端や枠の斜めの線が紛れ込んだ）
使い方: python btn_from_cd_0915.py [名前 ...]   （名前を省くと JOBS の全部。出力は tmp/btn_tpl/）
※ tmp/ 直下で動かすと tmp/inspect.py が Python の inspect を横取りして numpy が落ちる＝このファイルは tmp/btn/ に置く
"""
import os
import sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

DL = r"C:\Users\user\Downloads"
CD = os.path.join(DL, "Gemini_Generated_Image_1jgqey1jgqey1jgq.jpg")
FONT = r"C:\Windows\Fonts\NotoSansJP-VF.ttf"
FONT_FALLBACK = r"C:\Windows\Fonts\HGSoeiKakugothicUB_X0213(04).ttc"
OUTDIR = "tmp/btn_tpl"
FRAME_T, FRAME_B = 52, 496   # CDの画像の枠の上下の線（crop_btn_frame_0915 の実測）
CAPW = 230                   # 左の端（枠と斜めの線）として元の画像から借りる幅
TEXT_X, GAP, RIGHT_PAD = 172, 40, 156   # CDの字の左端・字とアイコンの間・アイコンの右の余白（実測）
INK_H = 238                  # CDの「最」の字の高さ（実測 156〜394）
MID_Y = 275                  # 字の中心の高さ
EXTRUDE = 16                 # 青い立体の深さ

# (出力名, 文字, アイコンの元画像 or None, アイコンを探し始める x, 元画像の枠の上下の線 (上, 下))
# 探す範囲＝x から右端まで・枠の上下の線の外まで＝元の字・枠の線・斜めの線は必ず範囲の端に触れるので捨てられる
UCHIWA = ("ChatGPT Image 2026年9月15日 20_14_02.png", 1880, (136, 561))
JOBS = [
    ("earplug", "ライブ用耳栓", "Gemini_Generated_Image_ay0wvgay0wvgay0w.jpg", 1460, (90, 491)),
    ("goods", "推し活グッズ", None, None, None),
    ("operaglass", "オペラグラス", "ChatGPT Image 2026年9月15日 20_22_57.png", 1745, (112, 599)),
    ("kansen", "観戦グッズ", "ChatGPT Image 2026年9月15日 20_25_18.png", 1620, (47, 641)),
    ("fes", "フェスの必需品", "Gemini_Generated_Image_tmb6vqtmb6vqtmb6.jpg", 1420, (90, 492)),
    ("hanabi", "花火の必需品", "Gemini_Generated_Image_imji0zimji0zimji.jpg", 1440, (84, 493), 1685),
    # ホテルとうちわは、ボタンの文字と画像の字がちがう＝ユーザーが決めるまで両方作る
    ("hotel_hoteru", "会場近くのホテルを探す", None, None, None),
    ("hotel_yado", "会場近くの宿を探す", None, None, None),
    ("uchiwa_oshi", "推しうちわを作る") + UCHIWA,
    ("uchiwa_ouen", "応援うちわを作る") + UCHIWA,
    # 9/15 夜 ユーザー「ぬりえ　も作って」（先に「塗り絵はなくていい」と言っていたのを取り消し）＝元の画像が無いので字だけ
    ("nurie", "ぬりえ", None, None, None),
    # 9/15 夜 ユーザー「チケットぴあも作ってあげて」＝字だけ（キーは PIA_DEF の「チケットぴあ」）
    ("pia", "チケットぴあ", None, None, None),
    # 9/15 夜 ユーザー「しまじろうグッズもつくってね」＝字だけ（キャラクターの絵は権利があるので使わない）
    ("shimajiro", "しまじろうグッズ", None, None, None),
]

# 9/15 夜 ユーザー「グッズで作って」＝子ども向けの作品ごとの「〇〇グッズ」。--kids-goods で tmp/btn_tpl/kids_goods.json の使える分だけ作る
# （名前は kg01〜。シンドバッドは検索で出るのが小説や別アニメ＝公演と関係ないので外す）
KG_EXCLUDE = {"シンドバッドグッズ"}
if '--kids-goods' in sys.argv:
    import json as _json
    _kg = [r for r in _json.load(open('tmp/btn_tpl/kids_goods.json', encoding='utf-8')) if r['ok'] and r['label'] not in KG_EXCLUDE]
    JOBS = [("kg%02d" % (i + 1), r['label'], None, None, None) for i, r in enumerate(_kg)]
    sys.argv = [a for a in sys.argv if a != '--kids-goods']


def load(path):
    return np.asarray(Image.open(path).convert('RGB')).astype(np.float32)


def blur(a, r):
    return np.asarray(Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255


def dilate(a, size):
    return np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(size))).astype(np.float32) / 255


src = load(CD)
H, W, _ = src.shape

# --- 字と光の場所（白い所を広げる）＝背景を拾う時に避ける／左の端を借りる時に消す
white = ((src[..., 0] > 150) & (src[..., 1] > 150) & (src[..., 2] > 150)).astype(np.float32)
white[:, 1240:] = 0          # CDの絵の側は左の端に関係しない
fg = dilate(white, 51)
fg_soft = np.clip(blur(fg, 10) * 1.3, 0, 1)

# --- 行ごとの背景色（x 200〜1240 の、字から離れた暗い所の中央値）
prof = np.full((H, 3), np.nan, np.float32)
mx = src.max(axis=2)
for y in range(H):
    if y < 100 or y > 468:
        # パネルの外側（枠の上下の水色の線がある行）＝字が無いので明るい所もそのまま拾う（外すと真ん中の枠の線が消えた）
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
    prof[100:469, c] = sm[100:469]   # ならすのはパネルの内側だけ（枠の線をぼかさない）

# --- 左の端（字の光は背景色に置きかえ、右へ行くほど背景色に溶かす）
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


def icon_patch(job):
    """元の画像からアイコンの「光」だけを取り出す（背景を引いた差分＝足し算で重ねる）"""
    name, text, path, x0, (ft, fb) = job[:5]
    fh = fb - ft
    isrc = load(os.path.join(DL, path))
    y0, y1, x1 = max(0, ft - 10), min(isrc.shape[0], fb + 11), isrc.shape[1]
    sub = isrc[y0:y1, x0:x1]
    h, w = sub.shape[:2]
    # 光の芯＝明るくて、緑か赤も強い所。ChatGPTの画像は背景の青が明るい（青だけ200超え）ので「青だけ明るい所」を外す
    # （水色の線＝緑が強い・白＝全部強い・花火のオレンジや赤＝赤が強い、は残る）
    bright_bg = np.median(sub[..., 2]) > 190
    core = ((sub.max(axis=2) > 200) & ((sub[..., 1] > 150) | (sub[..., 0] > 150))).astype(np.uint8)
    xmax = job[5] if len(job) > 5 else None
    n, lab, stats, _ = cv2.connectedComponentsWithStats(core, connectivity=8)
    keep = np.zeros((h, w), np.float32)
    dropped = np.zeros((h, w), np.float32)
    for i in range(1, n):
        x, y, bw, bh, area = stats[i]
        if x == 0 or y == 0 or x + bw >= w or y + bh >= h or area < 6 or (xmax is not None and x0 + x >= xmax):
            # 枠の端にくっついている塊＝元の字の端・枠の斜めの線／xmax より右＝斜めの線のかけら（花火で実測）
            dropped[lab == i] = 1
            continue
        keep[lab == i] = 1
    # アイコンのまわりの光も少し連れてくる。ただし捨てた塊（枠・斜めの線）のまわりは連れてこない（右端にかけらが残った）
    keep = np.clip(blur(dilate(keep, 31), 6) * 1.5, 0, 1) * (1 - dilate(dropped, 31))
    if xmax is not None:
        keep[:, max(0, xmax - x0):] = 0
    bg = cv2.medianBlur(sub.astype(np.uint8), 81).astype(np.float32)
    lum = lambda a: a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11
    if bright_bg:
        # 明るい青から色ごと引くと白い線が黄色っぽくなる＝明るさの差だけ取って、CDと同じ水色→白の光に塗り直す
        t = np.clip((lum(sub) - lum(bg)) / 180, 0, 1)[..., None]
        cyan, whitec = np.array((40, 150, 255), np.float32), np.array((255, 255, 255), np.float32)
        s = np.clip((t - 0.55) / 0.35, 0, 1)
        color = cyan * (1 - s) + whitec * s
        alpha = np.clip(t * 1.8, 0, 1)[..., 0] * keep
    else:
        # Geminiの画像は背景が紺でCDと近い＝元の色のまま、明るさの差の分だけ重ねる（引き算すると緑っぽくなった）
        color = sub
        alpha = np.clip((lum(sub) - lum(bg)) / 110, 0, 1) * keep
    yy, xx = np.nonzero(alpha > 0.02)
    ys_, xs_ = slice(yy.min(), yy.max() + 1), slice(xx.min(), xx.max() + 1)
    rgba = np.dstack([color[ys_, xs_], alpha[ys_, xs_][..., None] * 255])
    s = (FRAME_B - FRAME_T) / fh
    im = Image.fromarray(np.clip(rgba, 0, 255).astype(np.uint8), 'RGBA')
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    return np.asarray(im).astype(np.float32)


def build(job):
    name, text = job[0], job[1]
    tb = font.getbbox(text)
    tw = tb[2] - tb[0]
    icon = icon_patch(job) if job[2] else None
    if icon is not None:
        Wn = TEXT_X + tw + GAP + icon.shape[1] + RIGHT_PAD
    else:
        Wn = TEXT_X * 2 + tw
    T = make_template(Wn)
    M, Ms = text_masks(text, Wn, TEXT_X - tb[0])
    E = np.zeros_like(Ms)
    for d in range(1, EXTRUDE + 1):
        E = np.maximum(E, shift(Ms, round(d * 0.2), d))
    G = blur(np.maximum(Ms, E), 22)
    glow = np.array((30, 110, 255), np.float32)
    T = 255 - (255 - T) * (1 - (glow / 255) * (0.8 * G)[..., None])
    ext = vgrad((50, 120, 255), (12, 40, 170), INK_T, INK_B + EXTRUDE)
    T = T * (1 - E[..., None]) + ext * E[..., None]
    T = T * (1 - Ms[..., None]) + np.array((185, 230, 255), np.float32) * Ms[..., None]
    fill = vgrad((255, 255, 255), (190, 230, 248), INK_T, INK_B)
    T = T * (1 - M[..., None]) + fill * M[..., None]
    if icon is not None:
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
    print('%s ｜%s ｜字 %s %dpx ｜%dx88 ｜%dKB' % (name, text, fname, SIZE, small.width, os.path.getsize(os.path.join(OUTDIR, name + '_88.png')) // 1024))
    return full


names = sys.argv[1:]
fulls = [build(j) for j in JOBS if not names or j[0] in names]

# 見比べ用＝いちばん上に元の「最新のCD」、下に作ったもの（高さ120にそろえて縦に並べる）
ref = Image.open(CD).convert('RGB').crop((0, FRAME_T - 12, W, FRAME_B + 13))
rows = [ref] + fulls
rows = [r.resize((round(r.width * 120 / r.height), 120), Image.LANCZOS) for r in rows]
sheet = Image.new('RGB', (max(r.width for r in rows) + 40, sum(r.height + 20 for r in rows) + 20), (14, 14, 22))
y = 20
for r in rows:
    sheet.paste(r, (20, y)); y += r.height + 20
sheet.save(os.path.join(OUTDIR, 'sheet.png'))
print('sheet', sheet.size)
