# -*- coding: utf-8 -*-
"""『推しまで教えて』の MV（頭から58秒）をコードで描く。課金ゼロ。
  python tools/oshimade_mv.py --board          … 絵コンテ（場面ごとの1コマを並べた1枚）
  python tools/oshimade_mv.py --frame 12.3     … その時刻の1コマ
  python tools/oshimade_mv.py --render         … 全コマ描いて曲と合わせて mp4
歌詞の時刻は LINES（文字起こしで合わせる）。絵は render(t) の1本道＝どの時刻も同じ式で描く。
"""
import argparse
import math
import os
import random
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.stdout.reconfigure(encoding='utf-8')
W, H, FPS = 1080, 1920, 30
DUR = 68.76                       # 1曲まるごと（ユーザー 2026-09-29「曲を１曲全部使ってほしい」）
BEAT = 0.65                       # 実測 92BPM
OUT = 'tmp/video/oshimade'
SONG = os.path.join(OUT, 'song_full.mp3')
CHAR = 'tmp/video/flash_0924/char_cut.png'
FONT_B = r'C:\Windows\Fonts\YuGothB.ttc'
FONT_R = r'C:\Windows\Fonts\YuGothM.ttc'

PURPLE = (74, 20, 120)
DEEP = (22, 6, 44)
ACCENT = (224, 64, 251)
GOLD = (255, 214, 102)
WHITE = (255, 255, 255)
CYAN = (34, 230, 245)
PINK = (255, 80, 200)
LIME = (120, 255, 140)
NEON = [CYAN, PINK, GOLD, LIME, (170, 120, 255)]
CUT = lambda k: os.path.join(OUT, 'cut_%s.png' % k)     # 実際の OSHINAVI の画面から切った部品

# (開始秒, 歌詞, 場面) ＝ 文字起こしで合わせる。場面は下の SCENES の名前
LINES = [                          # 2026-09-29 faster-whisper(small) の単語時刻から
    (0.0, '推し活なら Oshinavi.jp', 'logo'),
    (3.8, '「推しに会いたい！」その気持ちを、もっとスムーズに。', 'hearts'),
    (10.5, 'ライブ・フェス・舞台のチケット情報を', 'genres'),
    (14.2, 'アーティスト名でサクッとかんたん検索', 'search'),
    (20.7, '販売ページへすぐアクセスできるから', 'button'),
    (25.7, '複数サイトを何度も探し回るストレスから解放', 'windows'),
    (31.9, '発売日までのカウントダウン表示で', 'countdown'),
    (35.9, '大切なチケットの買い逃しもしっかり防止', 'check'),
    (40.7, '気になるイベントをまとめてチェックして', 'cards'),
    (44.3, '次の現場へのワクワクをいつでもキープ', 'confetti'),
    (48.3, '推し活をもっと楽しく、もっと快適に', 'dance'),
    (53.3, 'チケット探しは Oshinavi.jp', 'tagline'),
    (56.0, 'おしなび！', 'chant'),                  # 56.0/57.0/58.9/60.8 の4回
    (63.4, 'Oshinavi.jp', 'end'),
]


def font(sz, bold=True):
    return ImageFont.truetype(FONT_B if bold else FONT_R, sz)


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def line_at(t):
    cur = LINES[0]
    for ln in LINES:
        if t >= ln[0]:
            cur = ln
    i = LINES.index(cur)
    end = LINES[i + 1][0] if i + 1 < len(LINES) else DUR
    return cur, t - cur[0], end - cur[0]


POSEDIR = os.path.join(OUT, 'poses')             # ユーザーのキャラシート（2026-09-29）を19枚に切ったもの
CLOSE = {'smile', 'wink', 'sexy', 'kiss', 'laugh', 'cool'}   # 顔のアップ＝下端が切れているので画面下に置く
CHOREO = {                                         # 場面ごとのポーズの順番（2拍ごとに次へ）
    'logo': ['front', 'wave', 'diag_f', 'hands_up'],
    'hearts': ['kiss', 'wink', 'smile', 'sexy', 'kiss'],
    'genres': ['diag_f', 'side_r', 'front', 'side_l'],
    'search': ['side_l', 'diag_f', 'front', 'wave', 'diag_f'],
    'button': ['wave', 'front', 'jump', 'diag_f'],
    'windows': ['back', 'diag_b', 'side_r', 'hands_up'],
    'countdown': ['sit_cross', 'sit_lean', 'sit_cross'],
    'check': ['cool', 'wink', 'smile'],
    'cards': ['crouch', 'kneel', 'crouch'],
    'confetti': ['laugh', 'wink', 'laugh', 'smile'],
    'dance': ['hands_up', 'jump', 'side_r', 'side_l', 'jump', 'wave', 'hands_up'],
    'tagline': ['diag_f', 'wave'],
    'chant': ['jump', 'hands_up', 'jump', 'wave', 'jump', 'hands_up', 'wink'],
    'end': ['front', 'kiss', 'wave'],
}
_pose = {}
CUR = {'pose': 'front', 'pop': 0.0}


def pose_img(name):
    if name not in _pose:
        _pose[name] = Image.open(os.path.join(POSEDIR, name + '.png')).convert('RGBA')
    return _pose[name]


_char = None


def char_img():
    global _char
    if _char is None:
        _char = Image.open(CHAR).convert('RGBA')
    return _char


def background(t):
    im = Image.new('RGB', (W, H), DEEP)
    d = ImageDraw.Draw(im)
    for y in range(0, H, 8):                       # 縦のグラデーション
        k = y / H
        c = tuple(int(DEEP[i] * (1 - k) + PURPLE[i] * k) for i in range(3))
        d.rectangle([0, y, W, y + 8], fill=c)
    rnd = random.Random(7)                          # きらきら（ネオン色・拍で明滅）
    pulse = 0.5 + 0.5 * math.cos(2 * math.pi * t / BEAT)
    for _ in range(90):
        x, y = rnd.randrange(W), rnd.randrange(H)
        ph = rnd.random()
        col = rnd.choice(NEON + [WHITE])
        a = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(2 * math.pi * (t / (BEAT * 2) + ph)))
        r = (3 + 5 * a * pulse) * rnd.uniform(0.7, 1.6)
        c = tuple(int(v * a) for v in col)
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)
        if rnd.random() < 0.35:                    # 十字の光
            L = r * 4
            d.line([x - L, y, x + L, y], fill=c, width=3)
            d.line([x, y - L, x, y + L], fill=c, width=3)
    return im


def paste_char(im, t, cx, bottom, h, tilt=True):
    """いまのポーズを拍に合わせて弾ませる。切り替わった瞬間はポンと大きく。大きさは場面で固定（寄らない）"""
    name = CUR['pose']
    c = pose_img(name)
    ph = (t % BEAT) / BEAT
    bounce = abs(math.sin(math.pi * ph)) * 28
    if name == 'jump':
        bounce = abs(math.sin(math.pi * ((t % (BEAT * 2)) / (BEAT * 2)))) * 160
    pop = 1 + 0.12 * max(0.0, 1 - CUR['pop'] / 0.18)
    if name in CLOSE:                               # 顔のアップ＝下端を画面の下（テロップの裏）へ
        h, bottom, cx, bounce = 900, H - 120, W / 2, bounce * 0.4
    ang = math.sin(2 * math.pi * t / (BEAT * 2)) * (4 if tilt else 0)
    hh = int(h * pop)
    r = hh / c.height
    c = c.resize((max(1, int(c.width * r)), hh), Image.LANCZOS).rotate(ang, resample=Image.BICUBIC, expand=True)
    im.paste(c, (int(cx - c.width / 2), int(bottom - c.height - bounce)), c)


def glow_text(im, xy, text, sz, fill=None, glow=CYAN, anchor='mm', stroke=0, grad=(CYAN, PINK)):
    """サイトの見出しと同じ＝水色→ピンクのグラデ文字＋ネオンの光。fill を渡すと単色"""
    f = font(sz)
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).text(xy, text, font=f, fill=glow + (255,), anchor=anchor, stroke_width=10, stroke_fill=glow + (255,))
    lay = lay.filter(ImageFilter.GaussianBlur(18))
    im.paste(lay, (0, 0), lay)
    im.paste(lay, (0, 0), lay)
    mask = Image.new('L', im.size, 0)
    ImageDraw.Draw(mask).text(xy, text, font=f, fill=255, anchor=anchor, stroke_width=4)
    ImageDraw.Draw(im).text(xy, text, font=f, fill=DEEP, anchor=anchor, stroke_width=6, stroke_fill=DEEP)
    if fill:
        im.paste(Image.new('RGB', im.size, fill), (0, 0), mask)
        return
    x0, y0, x1, y1 = mask.getbbox() or (0, 0, W, H)
    g = Image.new('RGB', (max(1, x1 - x0), 1))
    for i in range(g.width):
        k = i / max(1, g.width - 1)
        g.putpixel((i, 0), tuple(int(grad[0][c] * (1 - k) + grad[1][c] * k) for c in range(3)))
    g = g.resize((x1 - x0, y1 - y0))
    im.paste(g, (x0, y0), mask.crop((x0, y0, x1, y1)))


def place(im, key, cx, top, w, u=9, slide=0.0):
    """OSHINAVI の画面の部品を貼る。slide＞0 なら右から滑り込む"""
    c = Image.open(CUT(key)).convert('RGB')
    r = w / c.width
    c = c.resize((int(w), int(c.height * r)), Image.LANCZOS)
    x = int(cx - w / 2 + (1 - ease(u / slide)) * W if slide else cx - w / 2)
    glow = Image.new('RGBA', (c.width + 60, c.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([20, 20, c.width + 40, c.height + 40], 24, outline=CYAN + (255,), width=10)
    glow = glow.filter(ImageFilter.GaussianBlur(12))
    im.paste(glow, (x - 30, int(top) - 30), glow)
    im.paste(c, (x, int(top)))
    return int(top + c.height)


def telop(im, text, u):
    """画面下の歌詞テロップ。長い行は2行に割る"""
    if not text:
        return
    d = ImageDraw.Draw(im)
    f = font(56)
    parts = [text]
    if d.textlength(text, font=f) > W - 120:
        cut = min(range(len(text)), key=lambda i: abs(d.textlength(text[:i], font=f) - d.textlength(text[i:], font=f)))
        best = None                        # 区切りの字（、。を…）の直後で、真ん中にいちばん近い所で割る
        for j, ch in enumerate(text):
            if ch in '、。をでがにはのも' and len(text) * 0.3 < j < len(text) * 0.8:
                if best is None or abs(j + 1 - cut) < abs(best - cut):
                    best = j + 1
        if best:
            cut = best
        parts = [text[:cut], text[cut:]]
    a = int(255 * ease(u / 0.25))
    box = Image.new('RGBA', im.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(box)
    y0 = H - 150 - 80 * (len(parts) - 1)
    bd.rounded_rectangle([40, y0 - 60, W - 40, H - 90], 36, fill=(10, 4, 24, int(a * 0.85)), outline=CYAN + (a,), width=6)
    im.paste(box, (0, 0), box)
    for k, p in enumerate(parts):
        d.text((W / 2, y0 + 80 * k), p, font=f, fill=WHITE + (a,), anchor='mm', stroke_width=5, stroke_fill=(120, 0, 160))


# ---------- 場面ごとの小道具（u＝場面内の経過秒 / L＝場面の長さ）----------

def s_intro(im, t, u, L):
    k = ease(u / 1.5)
    glow_text(im, (W / 2, 520), '推しまで', int(40 + 90 * k))
    glow_text(im, (W / 2, 680), '教えて♪', int(40 + 90 * ease((u - 0.6) / 1.5)))
    paste_char(im, t, W / 2, 1650, 900)


def s_logo(im, t, u, L):
    place(im, 'hdr', W / 2, 150, 1000, u, slide=0.6)          # 本物のヘッダー
    glow_text(im, (W / 2, 620), '推し活なら', 96)
    s_ = 1 + 0.06 * math.sin(2 * math.pi * t / BEAT)
    glow_text(im, (W / 2, 780), 'Oshinavi.jp', int(140 * s_), fill=WHITE, glow=PINK)
    paste_char(im, t, W / 2, 1640, 760)


def heart(d, x, y, r, col):
    d.ellipse([x - r, y - r, x, y], fill=col)
    d.ellipse([x, y - r, x + r, y], fill=col)
    d.polygon([(x - r, y - r / 2 + 2), (x + r, y - r / 2 + 2), (x, y + r)], fill=col)


def s_hearts(im, t, u, L):
    d = ImageDraw.Draw(im)
    rnd = random.Random(3)
    for i in range(24):
        x = rnd.randrange(80, W - 80)
        sp = rnd.uniform(160, 320)
        y = 1500 - ((u + rnd.random() * 3) * sp) % 1400
        heart(d, x, y, rnd.randrange(22, 50), (255, rnd.randrange(80, 160), 200))
    glow_text(im, (W / 2, 330), '推しに会いたい！', 100)
    paste_char(im, t, W / 2 + 120, 1650, 860)


def card(im, x, y, w, h, title, sub, col):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([x, y, x + w, y + h], 28, fill=WHITE, outline=col, width=8)
    d.text((x + w / 2, y + h * 0.42), title, font=font(64), fill=col, anchor='mm')
    if sub:
        d.text((x + w / 2, y + h * 0.75), sub, font=font(36, False), fill=(90, 70, 110), anchor='mm')


def s_genres(im, t, u, L):
    glow_text(im, (W / 2, 250), 'ライブ・フェス・舞台', 92)
    place(im, 'pills', W / 2, 360, 1000, u, slide=0.5)       # 本物のジャンルのボタン
    paste_char(im, t, W / 2, 1650, 760)


def s_search(im, t, u, L):
    glow_text(im, (W / 2, 260), 'アーティスト名で検索', 90)
    top = 380
    bottom = place(im, 'search', W / 2, top, 1000)            # 本物の検索窓
    d = ImageDraw.Draw(im)
    h = bottom - top
    d.rectangle([150, top + h * 0.25, 990, top + h * 0.75], fill=(14, 14, 18))   # 置き文字を隠して打ち込む
    q = '推しの名前'
    n = min(len(q), int(u / 0.3))
    cur = '|' if int(u * 3) % 2 == 0 else ''
    d.text((165, top + h / 2), q[:n] + cur, font=font(64), fill=WHITE, anchor='lm')
    if u > 2.0:
        place(im, 'card2badges', W / 2, 600, 820, u - 2.0, slide=0.5)
    paste_char(im, t, W / 2 + 250, 1650, 640)


def s_button(im, t, u, L):
    d = ImageDraw.Draw(im)
    press = 1 - 0.08 * max(0, math.sin(2 * math.pi * t / BEAT))
    bw, bh = int(640 * press), int(170 * press)
    d.rounded_rectangle([W / 2 - bw / 2, 380 - bh / 2, W / 2 + bw / 2, 380 + bh / 2], 85, fill=ACCENT)
    d.text((W / 2, 380), '販売ページへ ▶', font=font(66), fill=WHITE, anchor='mm')
    for i in range(3):                                # 飛んでいく矢印
        x = (u * 600 + i * 360) % (W + 200) - 100
        d.polygon([(x, 560), (x + 60, 600), (x, 640)], fill=GOLD)
    paste_char(im, t, W / 2, 1650, 860)


def s_windows(im, t, u, L):
    d = ImageDraw.Draw(im)
    fade = 1 - ease((u - L * 0.55) / 0.6)             # 後半で消える＝解放
    rnd = random.Random(11)
    for i in range(7):
        a = u * rnd.uniform(0.8, 1.6) + i
        x = W / 2 + math.cos(a) * 340 * fade - 170
        y = 600 + math.sin(a * 1.3) * 300 * fade - 110
        if fade > 0.05:
            d.rounded_rectangle([x, y, x + 340 * fade, y + 220 * fade], 16, fill=(235, 235, 245), outline=(120, 120, 140), width=4)
            d.rectangle([x, y, x + 340 * fade, y + 36 * fade], fill=(120, 120, 140))
    if fade < 0.5:
        glow_text(im, (W / 2, 520), '解放！', 150, glow=GOLD)
    paste_char(im, t, W / 2, 1650, 860)


def s_countdown(im, t, u, L):
    glow_text(im, (W / 2, 250), '発売まで カウントダウン', 84)
    place(im, 'card2badges', W / 2, 360, 900, u, slide=0.4)   # 本日発売＝赤／販売中＝緑（本物の色）
    n = max(1, 5 - int(u / (BEAT * 2)))
    s_ = 1 + 0.15 * (1 - ((u % (BEAT * 2)) / (BEAT * 2)))
    glow_text(im, (W / 2 - 160, 1260), 'あと%d日' % n, int(130 * s_), grad=(GOLD, PINK), glow=PINK)
    paste_char(im, t, W / 2 + 300, 1650, 600)


def s_check(im, t, u, L):
    glow_text(im, (W / 2, 250), '買い逃し防止！', 110, grad=(LIME, CYAN), glow=LIME)
    bottom = place(im, 'card1', W / 2, 360, 780, u, slide=0.4)
    d = ImageDraw.Draw(im)
    k = ease((u - 0.8) / 0.4)                                 # 大きなチェック
    if k > 0:
        x, y = W / 2 + 220, 700
        d.line([(x - 90, y), (x - 20, y + 80 * k), (x - 20 + 150 * k, y + 80 - 170 * k)], fill=LIME, width=30)
    paste_char(im, t, W / 2 - 280, 1650, 620)


def s_cards(im, t, u, L):
    glow_text(im, (W / 2, 240), 'まとめてチェック', 104)
    for i, k in enumerate(['card1', 'card3', 'card2badges']):
        if u > i * 0.6:
            place(im, k, W / 2 + (i - 1) * 40, 340 + i * 110, 760, u - i * 0.6, slide=0.4)
    paste_char(im, t, W / 2 + 280, 1650, 600)


def s_confetti(im, t, u, L):
    d = ImageDraw.Draw(im)
    rnd = random.Random(5)
    for i in range(120):
        x = rnd.randrange(W)
        y = (rnd.random() * H + u * rnd.uniform(200, 500)) % H
        c = rnd.choice([GOLD, ACCENT, (0, 200, 255), (255, 120, 160), WHITE])
        a = u * 5 + i
        d.polygon([(x + 14 * math.cos(a), y + 14 * math.sin(a)), (x - 14 * math.cos(a), y - 14 * math.sin(a)), (x + 8, y + 8)], fill=c)
    glow_text(im, (W / 2, 400), 'ワクワク！', 130, glow=GOLD)
    paste_char(im, t, W / 2, 1650, 880)


def s_dance(im, t, u, L):
    x = W / 2 + math.sin(2 * math.pi * u / (BEAT * 4)) * 200    # 左右にステップ（大きさは同じ）
    glow_text(im, (W / 2, 380), 'もっと楽しく', 110)
    glow_text(im, (W / 2, 530), 'もっと快適に', 110, glow=GOLD)
    paste_char(im, t, x, 1650, 860)


def s_end(im, t, u, L):
    glow_text(im, (W / 2, 330), 'チケット探しは', 90)
    s = 1 + 0.05 * math.sin(2 * math.pi * t / BEAT)
    glow_text(im, (W / 2, 520), 'Oshinavi.jp', int(150 * s), fill=WHITE, glow=(255, 255, 255))  # URLは光る白
    paste_char(im, t, W / 2, 1650, 900)


def s_tagline(im, t, u, L):
    glow_text(im, (W / 2, 330), 'チケット探しは', 96)
    glow_text(im, (W / 2, 500), 'Oshinavi.jp', 150, fill=WHITE, glow=PINK)
    paste_char(im, t, W / 2, 1650, 800)


def s_chant(im, t, u, L):
    hits = [0.0, 1.0, 2.9, 4.8]                         # 「おしなび！」の4回（曲の56.0/57.0/58.9/60.8）
    last = max([h for h in hits if u >= h] or [0])
    k = u - last
    s_ = 1 + 0.35 * max(0.0, 1 - k / 0.35)
    cols = [(CYAN, PINK), (GOLD, PINK), (LIME, CYAN), (PINK, GOLD)]
    glow_text(im, (W / 2, 420), 'おしなび！', int(150 * s_), grad=cols[hits.index(last)], glow=cols[hits.index(last)][1])
    s_confetti_only(im, u)
    paste_char(im, t, W / 2, 1650, 820)


def s_confetti_only(im, u):
    d = ImageDraw.Draw(im)
    rnd = random.Random(9)
    for i in range(80):
        x = rnd.randrange(W)
        y = (rnd.random() * H + u * rnd.uniform(200, 500)) % H
        c = rnd.choice(NEON)
        a = u * 5 + i
        d.polygon([(x + 14 * math.cos(a), y + 14 * math.sin(a)), (x - 14 * math.cos(a), y - 14 * math.sin(a)), (x + 8, y + 8)], fill=c)


SCENES = {'tagline': s_tagline, 'chant': s_chant, 'intro': s_intro, 'logo': s_logo, 'hearts': s_hearts, 'genres': s_genres, 'search': s_search,
          'button': s_button, 'windows': s_windows, 'countdown': s_countdown, 'check': s_check,
          'cards': s_cards, 'confetti': s_confetti, 'dance': s_dance, 'end': s_end}


def render(t):
    im = background(t)
    (start, text, scene), u, L = line_at(t)
    seq = CHOREO.get(scene, ['front'])
    step = BEAT * 2
    CUR['pose'] = seq[int(u / step) % len(seq)]
    CUR['pop'] = u % step
    SCENES[scene](im, t, u, L)
    telop(im, text, u)
    if t > DUR - 1.8:                               # 曲の終わり（67秒〜）に合わせて暗転
        k = (t - (DUR - 1.8)) / 1.8
        im = Image.blend(im, Image.new('RGB', im.size, DEEP), min(1.0, k * 0.85))
    return im


def board(path):
    cols, sw = 5, 216
    shots = [(ln[0] + 1.6, ln[2]) for ln in LINES]
    rows = (len(shots) + cols - 1) // cols
    sh = int(sw * H / W)
    b = Image.new('RGB', (cols * (sw + 12) + 12, rows * (sh + 50) + 12), (30, 30, 30))
    d = ImageDraw.Draw(b)
    for i, (tt, name) in enumerate(shots):
        x, y = 12 + (i % cols) * (sw + 12), 12 + (i // cols) * (sh + 50)
        b.paste(render(tt).resize((sw, sh), Image.LANCZOS), (x, y))
        d.text((x + 4, y + sh + 6), '%d:%04.1f %s' % (int(tt // 60), tt % 60, name), font=font(20, False), fill=WHITE)
    b.save(path)
    print('絵コンテ', path, b.size)


def render_all(out):
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    p = subprocess.Popen([ff, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
                          '-i', SONG, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-c:a', 'aac', '-b:a', '192k',
                          '-shortest', out], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    n = int(DUR * FPS)
    for i in range(n):
        p.stdin.write(render(i / FPS).tobytes())
        if i % 150 == 0:
            print('  %d/%d' % (i, n), flush=True)
    p.stdin.close()
    p.wait()
    print('動画', out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--board', action='store_true')
    ap.add_argument('--frame', type=float)
    ap.add_argument('--render', action='store_true')
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.board:
        board(os.path.join(OUT, 'storyboard.png'))
    if a.frame is not None:
        render(a.frame).save(os.path.join(OUT, 'frame_%05.1f.png' % a.frame))
    if a.render:
        render_all(os.path.join(OUT, 'oshimade_full.mp4'))
