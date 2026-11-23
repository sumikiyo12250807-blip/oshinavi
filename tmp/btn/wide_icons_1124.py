# -*- coding: utf-8 -*-
"""横長ボタン（宿ボタンが型）に、宿の「夜のホテル」と同じ描き方の絵を付ける（2026-11-24 朝）
すちこ「うちわの絵とかオペラグラスのえを書いて」→「推し活グッツにペンライト何本か光らせるとかCDの絵も　Amazonミュージックはイヤフォンで聞いてる人影とか　ボタンが目立つように考えて」
描き方＝後ろに青い光の輪・暗い紺の影絵（ふちがほんのり青く光る）・灯る所は色つきで光がにじむ
目立たせ方＝絵を大きく（高さ 100px 近く）・灯りの色を絵ごとに（ペンライトはピンク・水色・黄・紫）・にじみを強め
出力＝tmp/btn_tpl/wide_<name>.png"""
import math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
os.chdir('C:/Users/user/oshinavi')
SRC = 'img/btn_hotel_wide.png'
FONT = r'C:\Windows\Fonts\NotoSansJP-VF.ttf'
OUT = 'tmp/btn_tpl'
SIL = (6, 16, 44, 255)
YEL = (255, 236, 90, 255)
PINK = (255, 92, 190, 255)
CYAN = (80, 230, 255, 255)
VIO = (190, 120, 255, 255)
WHITE = (255, 255, 240, 255)
HALO = (48, 84, 150)
base = Image.open(SRC).convert('RGBA')
W, H = base.size
px = base.load()
X0, X1, Y0, Y1 = 34, 920, 10, H - 10
col = []
for y in range(H):
    rs = [px[x, y] for x in range(40, 56)]
    col.append(tuple(sum(c[i] for c in rs) // len(rs) for i in range(4)))
CX, CY = 814, 62
S = 4
IW, IH = 220, H
BX = CX - IW // 2


def blank():
    im = base.copy()
    p = im.load()
    for x in range(X0, X1):
        for y in range(Y0, Y1):
            r, g, b, a = col[y]
            d = math.hypot((x - CX) / 1.2, y - CY)
            k = max(0.0, 1 - d / 90) ** 1.2
            p[x, y] = (int(r + (HALO[0] - r) * k), int(g + (HALO[1] - g) * k), int(b + (HALO[2] - b) * k), a)
    return im


def P(x, y):
    return ((x - BX) * S, y * S)


def R(x0, y0, x1, y1):
    a, b = P(x0, y0); c, d = P(x1, y1)
    return [a, b, c, d]


def heart(d, cx, cy, s, fill):
    pts = []
    for i in range(90):
        t = 2 * math.pi * i / 90
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append(P(cx + x * s / 16, cy + y * s / 16))
    d.polygon(pts, fill=fill)


def rot_poly(cx, cy, w, h, ang, y_off=0):
    """中心 (cx,cy)・幅 w・高さ h の棒を ang 度かたむけた4点"""
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for dx, dy in ((-w / 2, -h / 2 + y_off), (w / 2, -h / 2 + y_off), (w / 2, h / 2 + y_off), (-w / 2, h / 2 + y_off)):
        pts.append(P(cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    return pts


# ── 絵 ──
def draw_uchiwa(sd, ld):
    sd.rounded_rectangle(R(811, 78, 818, 112), radius=3 * S, fill=SIL)
    ld.ellipse(R(772, 8, 856, 92), fill=PINK)                     # ふちがピンクに光る
    sd.ellipse(R(777, 13, 851, 87), fill=SIL)
    heart(ld, 814, 50, 24, YEL)


def draw_opera(sd, ld):
    sd.line([P(846, 70), P(880, 110)], fill=SIL, width=7 * S)
    sd.rounded_rectangle(R(800, 32, 828, 52), radius=5 * S, fill=SIL)
    for x in (788, 840):
        sd.ellipse(R(x - 28, 30, x + 28, 86), fill=SIL)
        ld.ellipse(R(x - 18, 40, x + 18, 76), fill=YEL)
        ld.ellipse(R(x - 9, 47, x + 1, 57), fill=WHITE)


def draw_goods(sd, ld):
    # ペンライト4本（扇に開いて・先が色とりどりに光る）
    for ang, c in ((-34, PINK), (-12, CYAN), (12, YEL), (34, VIO)):
        sd.polygon(rot_poly(814, 100, 9, 40, ang, y_off=-20), fill=SIL)        # 持ち手
        ld.polygon(rot_poly(814, 100, 11, 52, ang, y_off=-66), fill=c)         # 光る棒
        ld.polygon(rot_poly(814, 100, 5, 46, ang, y_off=-66), fill=WHITE)      # 芯の白


def draw_earplug(sd, ld):
    for x, tilt, c in ((794, -14, YEL), (836, 14, CYAN)):
        body = Image.new('RGBA', (IW * S, IH * S), (0, 0, 0, 0))
        bd = ImageDraw.Draw(body)
        bd.rounded_rectangle(R(x - 14, 22, x + 14, 92), radius=13 * S, fill=c)
        for yy in (42, 60, 76):
            bd.line([P(x - 13, yy), P(x + 13, yy)], fill=(0, 0, 0, 70), width=S)
        body = body.rotate(tilt, center=P(x, 57), resample=Image.BICUBIC)
        ld._image.alpha_composite(body)


def draw_kansen(sd, ld):
    sd.polygon([P(772, 48), P(842, 18), P(842, 98), P(772, 72)], fill=SIL)
    sd.rounded_rectangle(R(760, 46, 778, 74), radius=4 * S, fill=SIL)
    sd.line([P(798, 76), P(804, 106)], fill=SIL, width=6 * S)
    ld.polygon([P(838, 22), P(844, 20), P(844, 96), P(838, 94)], fill=YEL)
    for r, c in ((14, YEL), (26, CYAN)):
        ld.arc(R(852 - r, 58 - r, 852 + r, 58 + r), -50, 50, fill=c, width=5 * S)


def draw_cd(sd, ld):
    # ケースの影絵の上に、虹色に光る盤
    sd.rounded_rectangle(R(764, 18, 834, 98), radius=4 * S, fill=SIL)
    ld.ellipse(R(830 - 44, 58 - 44, 830 + 44, 58 + 44), fill=(205, 220, 245, 255))       # 銀の盤
    for a0, c in ((200, PINK), (230, VIO), (20, CYAN), (50, YEL)):                       # 虹色のつや（向かい合わせに2本ずつ）
        ld.pieslice(R(830 - 42, 58 - 42, 830 + 42, 58 + 42), a0, a0 + 26, fill=c)
    ld.ellipse(R(830 - 16, 58 - 16, 830 + 16, 58 + 16), fill=(225, 235, 250, 255))
    sd.ellipse(R(830 - 13, 58 - 13, 830 + 13, 58 + 13), fill=(120, 140, 180, 255))
    sd.ellipse(R(830 - 6, 58 - 6, 830 + 6, 58 + 6), fill=SIL)


def draw_music(sd, ld):
    # 横顔の人影がヘッドホンで聴いている・音符が光って浮かぶ
    sd.ellipse(R(770, 22, 822, 78), fill=SIL)                           # 頭
    sd.polygon([P(812, 46), P(826, 58), P(814, 62)], fill=SIL)           # 鼻
    sd.rounded_rectangle(R(780, 70, 808, 92), radius=6 * S, fill=SIL)    # 首
    sd.ellipse(R(752, 84, 838, 132), fill=SIL)                          # 肩
    ld.arc(R(764, 12, 828, 76), 190, 350, fill=CYAN, width=6 * S)        # ヘッドホンのつる
    ld.rounded_rectangle(R(778, 40, 796, 64), radius=7 * S, fill=CYAN)   # 耳あて
    for x, y, c in ((846, 34, YEL), (866, 60, PINK)):
        ld.ellipse(R(x - 8, y + 6, x + 6, y + 16), fill=c)
        ld.rounded_rectangle(R(x + 2, y - 18, x + 6, y + 12), radius=S, fill=c)
        ld.polygon([P(x + 2, y - 18), P(x + 14, y - 12), P(x + 14, y - 6), P(x + 6, y - 10)], fill=c)


JOBS = [('uchiwa', '推しうちわを作る', draw_uchiwa), ('operaglass', 'オペラグラスを見る', draw_opera), ('goods', '推し活グッズを見る', draw_goods),
        ('earplug', 'ライブ用耳栓を見る', draw_earplug), ('kansen', '観戦グッズを見る', draw_kansen), ('cd', '予習する（最新CD）', draw_cd),
        ('amazonmusic', 'Amazon Musicで聴く', draw_music)]


def font(size):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([900])
    except Exception:
        pass
    return f


def make(text, fn):
    im = blank()
    sil = Image.new('RGBA', (IW * S, IH * S), (0, 0, 0, 0))
    lit = Image.new('RGBA', (IW * S, IH * S), (0, 0, 0, 0))
    fn(ImageDraw.Draw(sil), ImageDraw.Draw(lit))
    g = lit.filter(ImageFilter.GaussianBlur(8 * S))                    # 灯りと同じ色でにじむ
    ga = g.split()[3].point(lambda v: min(255, int(v * 2.2)))
    g.putalpha(ga)
    rim = Image.new('RGBA', sil.size, (80, 125, 210, 255))
    rim.putalpha(sil.split()[3].filter(ImageFilter.MaxFilter(9)))
    icon = Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(g, rim), sil), lit)
    icon = icon.resize((IW, IH), Image.LANCZOS)
    clip = Image.new('L', (IW, IH), 0)
    ImageDraw.Draw(clip).rectangle([0, Y0, IW, Y1 - 1], fill=255)     # 枠の外へはみ出さない
    a = icon.split()[3]
    icon.putalpha(Image.composite(a, Image.new('L', a.size, 0), clip))
    im.alpha_composite(icon, (BX, 0))
    d = ImageDraw.Draw(im)
    L, Rr = 60, 716
    size = 62
    f = font(size)
    while d.textlength(text, font=f) > (Rr - L) and size > 36:
        size -= 2
        f = font(size)
    tw = d.textlength(text, font=f)
    x = L + ((Rr - L) - tw) / 2
    bb = d.textbbox((0, 0), text, font=f)
    y = H / 2 - (bb[1] + bb[3]) / 2
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((x + 2, y + 4), text, font=f, fill=(0, 0, 0, 190))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(2)))
    ImageDraw.Draw(im).text((x, y), text, font=f, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(10, 18, 50, 255))
    return im


for name, text, fn in JOBS:
    out = '%s/wide_%s.png' % (OUT, name)
    make(text, fn).quantize(256).save(out, optimize=True)
    print(out, os.path.getsize(out))
