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
DUR = 58.0
BEAT = 0.65                       # 実測 92BPM
OUT = 'tmp/video/oshimade'
SONG = os.path.join(OUT, 'song_0_58.mp3')
CHAR = 'tmp/video/flash_0924/char_cut.png'
FONT_B = r'C:\Windows\Fonts\YuGothB.ttc'
FONT_R = r'C:\Windows\Fonts\YuGothM.ttc'

PURPLE = (74, 20, 120)
DEEP = (22, 6, 44)
ACCENT = (224, 64, 251)
GOLD = (255, 214, 102)
WHITE = (255, 255, 255)

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
    (53.3, 'チケット探しは Oshinavi.jp', 'end'),
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
    rnd = random.Random(7)                          # きらきら（拍で明滅）
    pulse = 0.5 + 0.5 * math.cos(2 * math.pi * t / BEAT)
    for _ in range(70):
        x, y = rnd.randrange(W), rnd.randrange(H)
        ph = rnd.random()
        a = 0.3 + 0.7 * (0.5 + 0.5 * math.sin(2 * math.pi * (t / (BEAT * 2) + ph)))
        r = 2 + 3 * a * pulse
        col = tuple(int(v * a) for v in (GOLD if rnd.random() < 0.4 else WHITE))
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    return im


def paste_char(im, t, cx, bottom, h, tilt=True):
    """拍に合わせて弾む。大きさは場面ごとに固定（寄らない）"""
    ph = (t % BEAT) / BEAT
    bounce = abs(math.sin(math.pi * ph)) * 28
    ang = math.sin(2 * math.pi * t / (BEAT * 2)) * (5 if tilt else 0)
    c = char_img()
    r = h / c.height
    c = c.resize((int(c.width * r), h), Image.LANCZOS).rotate(ang, resample=Image.BICUBIC, expand=True)
    im.paste(c, (int(cx - c.width / 2), int(bottom - c.height - bounce)), c)


def glow_text(im, xy, text, sz, fill=WHITE, glow=ACCENT, anchor='mm', stroke=0):
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).text(xy, text, font=font(sz), fill=glow + (255,), anchor=anchor, stroke_width=stroke + 6, stroke_fill=glow + (255,))
    lay = lay.filter(ImageFilter.GaussianBlur(14))
    im.paste(lay, (0, 0), lay)
    ImageDraw.Draw(im).text(xy, text, font=font(sz), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=PURPLE)


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
    bd.rounded_rectangle([40, y0 - 60, W - 40, H - 90], 36, fill=(20, 0, 40, int(a * 0.7)))
    im.paste(box, (0, 0), box)
    for k, p in enumerate(parts):
        d.text((W / 2, y0 + 80 * k), p, font=f, fill=WHITE + (a,), anchor='mm', stroke_width=4, stroke_fill=PURPLE)


# ---------- 場面ごとの小道具（u＝場面内の経過秒 / L＝場面の長さ）----------

def s_intro(im, t, u, L):
    k = ease(u / 1.5)
    glow_text(im, (W / 2, 520), '推しまで', int(40 + 90 * k))
    glow_text(im, (W / 2, 680), '教えて♪', int(40 + 90 * ease((u - 0.6) / 1.5)))
    paste_char(im, t, W / 2, 1650, 900)


def s_logo(im, t, u, L):
    glow_text(im, (W / 2, 380), '推し活なら', 90)
    s = 1 + 0.06 * math.sin(2 * math.pi * t / BEAT)
    glow_text(im, (W / 2, 560), 'Oshinavi.jp', int(130 * s), glow=GOLD)
    paste_char(im, t, W / 2, 1640, 880)


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
    names = [('ライブ', (224, 64, 251)), ('フェス', (255, 140, 0)), ('舞台', (0, 150, 200))]
    for i, (n, c) in enumerate(names):
        k = ease((u - i * BEAT) / 0.5)
        x = int(-400 + (80 + i * 320 + 400) * k)
        card(im, x, 260 + i * 40, 300, 220, n, '', c)
    paste_char(im, t, W / 2, 1650, 860)


def s_search(im, t, u, L):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([90, 300, W - 90, 440], 70, fill=WHITE, outline=ACCENT, width=8)
    q = 'アーティスト名'
    n = min(len(q), int(u / 0.25))
    cur = '|' if int(u * 3) % 2 == 0 else ''
    d.text((170, 370), '🔍' if False else '', font=font(60), fill=PURPLE, anchor='lm')
    d.ellipse([140, 340, 200, 400], outline=PURPLE, width=8)
    d.line([192, 392, 222, 422], fill=PURPLE, width=10)
    d.text((250, 370), q[:n] + cur, font=font(64), fill=PURPLE, anchor='lm')
    if u > 2.2:
        for i in range(3):
            k = ease((u - 2.2 - i * 0.2) / 0.4)
            y = 480 + i * 120
            d.rounded_rectangle([110, y, int(110 + (W - 220) * k), y + 100], 20, fill=(255, 255, 255, 230))
            if k > 0.9:
                d.text((150, y + 50), ['東京 11/15 〜発売まであと3日', '大阪 11/22 〜発売中', '福岡 12/6 〜発売まであと10日'][i], font=font(40, False), fill=PURPLE, anchor='lm')
    paste_char(im, t, W / 2 + 180, 1650, 820)


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
    d = ImageDraw.Draw(im)
    n = max(1, 5 - int(u / (BEAT * 2)))
    d.rounded_rectangle([200, 250, W - 200, 700], 50, fill=WHITE, outline=GOLD, width=12)
    d.text((W / 2, 340), '発売まで あと', font=font(60), fill=PURPLE, anchor='mm')
    s = 1 + 0.15 * (1 - ((u % (BEAT * 2)) / (BEAT * 2)))
    d.text((W / 2, 540), '%d日' % n, font=font(int(170 * s)), fill=ACCENT, anchor='mm')
    paste_char(im, t, W / 2, 1650, 820)


def s_check(im, t, u, L):
    d = ImageDraw.Draw(im)
    for i, s in enumerate(['発売日', '締切', '会場']):
        y = 300 + i * 150
        d.rounded_rectangle([160, y, W - 160, y + 120], 30, fill=WHITE)
        d.text((260, y + 60), s, font=font(60), fill=PURPLE, anchor='lm')
        k = ease((u - 0.5 - i * BEAT) / 0.3)
        if k > 0:
            d.line([(W - 330, y + 60), (W - 290, y + 100 - (1 - k) * 40), (W - 290 + 80 * k, y + 20 + (1 - k) * 80)], fill=(40, 190, 90), width=16)
    paste_char(im, t, W / 2, 1650, 820)


def s_cards(im, t, u, L):
    for i in range(4):
        k = ease((u - i * 0.4) / 0.5)
        y = int(-300 + (260 + i * 70 + 300) * k)
        card(im, 150 + i * 20, y, W - 300, 200, ['11/15 東京', '11/22 大阪', '12/6 福岡', '12/20 名古屋'][i], '発売前', [ACCENT, (255, 140, 0), (0, 150, 200), (40, 190, 90)][i])
    paste_char(im, t, W / 2, 1650, 800)


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


SCENES = {'intro': s_intro, 'logo': s_logo, 'hearts': s_hearts, 'genres': s_genres, 'search': s_search,
          'button': s_button, 'windows': s_windows, 'countdown': s_countdown, 'check': s_check,
          'cards': s_cards, 'confetti': s_confetti, 'dance': s_dance, 'end': s_end}


def render(t):
    im = background(t)
    (start, text, scene), u, L = line_at(t)
    SCENES[scene](im, t, u, L)
    telop(im, text, u)
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
        render_all(os.path.join(OUT, 'oshimade_0_58.mp4'))
