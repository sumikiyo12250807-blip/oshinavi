# -*- coding: utf-8 -*-
"""X投稿の「主役」1組につける10秒の縦動画をコードで描く（課金ゼロ・2026-10-03 新設）。
部品は tools/oshimade_mv.py（背景・ネオン文字・キャラのポーズ・本物のOSHINAVI画面の切り抜き）をそのまま使う。
  python tools/shuyaku_video.py spec.json --board    … 4場面の絵コンテ（spec と同じ場所に _board.png）
  python tools/shuyaku_video.py spec.json --render   … mp4（曲『推しまで教えて』の頭10秒）
spec.json = {"when": "明日 10/5(月) 10:00", "kind": "一般発売", "name": "西川貴教",
             "sub": "Zepp Tour 2026", "lines": ["10/4(日) Zepp Nagoya"], "out": "tmp/video/shuyaku/nishikawa.mp4"}
🚨 文字は売り場・公式で裏取りした事実だけ（投稿の本文と同じ）。アーティストの写真は使わない（権利）。
"""
import argparse, io, json, math, os, subprocess, sys
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')
ROOT = 'C:/Users/user/oshinavi'
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import oshimade_mv as M                       # noqa: E402

W, H, FPS, DUR, BEAT = M.W, M.H, M.FPS, 10.0, M.BEAT
SCENES = [(0.0, 'when'), (2.6, 'who'), (6.4, 'search'), (8.4, 'url')]
CHOREO = {'when': ['jump', 'hands_up', 'jump'], 'who': ['diag_f', 'wave', 'front'],
          'search': ['side_l', 'diag_f'], 'url': ['wave', 'kiss']}


def fit(text, sz, maxw):
    d = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    while sz > 36 and d.textlength(text, font=M.font(sz)) > maxw:
        sz -= 4
    return sz


def wrap(text, sz, maxw):
    d = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    out, cur = [], ''
    for ch in text:
        if d.textlength(cur + ch, font=M.font(sz)) > maxw:
            out.append(cur); cur = ch
        else:
            cur += ch
    return out + ([cur] if cur else [])


def scene_at(t):
    cur = SCENES[0]
    for s in SCENES:
        if t >= s[0]:
            cur = s
    i = SCENES.index(cur)
    end = SCENES[i + 1][0] if i + 1 < len(SCENES) else DUR
    return cur[1], t - cur[0], end - cur[0]


def render(t, S):
    im = M.background(t)
    name, u, L = scene_at(t)
    seq = CHOREO[name]
    M.CUR['pose'] = seq[int(u / (BEAT * 2)) % len(seq)]
    M.CUR['pop'] = u % (BEAT * 2)
    d = ImageDraw.Draw(im)
    if name == 'when':
        k = M.ease(u / 0.8)
        M.glow_text(im, (W / 2, 330), S['when'], fit(S['when'], int(40 + 60 * k), 1000))
        M.glow_text(im, (W / 2, 520), S['kind'], int(60 + 70 * M.ease((u - 0.4) / 0.8)), grad=(M.GOLD, M.PINK), glow=M.PINK)
        M.paste_char(im, t, W / 2, 1700, 950)
    elif name == 'who':
        sz = fit(S['name'], 130, 1000)
        M.glow_text(im, (W / 2, 260), S['name'], int(sz * (0.6 + 0.4 * M.ease(u / 0.5))))
        y = 420
        for ln in wrap(S.get('sub', ''), 58, 960)[:3]:
            d.text((W / 2, y), ln, font=M.font(58), fill=M.WHITE, anchor='mm', stroke_width=5, stroke_fill=(90, 0, 140)); y += 78
        y += 30
        for i, ln in enumerate(S.get('lines', [])[:5]):
            a = M.ease((u - 0.5 - 0.35 * i) / 0.4)
            if a <= 0:
                continue
            x = W / 2 + (1 - a) * 400
            d.rounded_rectangle([x - 470, y - 48, x + 470, y + 48], 30, fill=(14, 6, 34), outline=M.CYAN, width=5)
            d.text((x, y), ln, font=M.font(fit(ln, 50, 880)), fill=M.WHITE, anchor='mm'); y += 120
        M.paste_char(im, t, W / 2 + 270, 1820, 700)
    elif name == 'search':
        M.glow_text(im, (W / 2, 250), 'OSHINAVIで検索', 90)
        top = 380
        bottom = M.place(im, 'search', W / 2, top, 1000)
        h = bottom - top
        d.rectangle([150, top + h * 0.25, 990, top + h * 0.75], fill=(14, 14, 18))
        q = S['name']
        n = min(len(q), int(u / 0.12))
        d.text((165, top + h / 2), q[:n] + ('|' if int(u * 3) % 2 == 0 else ''), font=M.font(fit(q, 64, 800)), fill=M.WHITE, anchor='lm')
        if u > 0.9:                                   # 🚨切り抜きのカード（別公演の日付入り）は使わない＝spec の中身だけで描く
            a = M.ease((u - 0.9) / 0.4)
            x0 = 110 + (1 - a) * W
            d.rounded_rectangle([x0, 640, x0 + 860, 1000], 24, fill=(24, 24, 30), outline=(70, 70, 80), width=3)
            d.text((x0 + 40, 700), S['name'], font=M.font(fit(S['name'], 52, 780)), fill=M.WHITE, anchor='lm')
            d.rounded_rectangle([x0 + 40, 760, x0 + 260, 820], 12, fill=(230, 50, 70))
            d.text((x0 + 150, 790), '明日発売', font=M.font(36), fill=M.WHITE, anchor='mm')
            d.text((x0 + 40, 880), '%s %s' % (S['when'].replace('明日 ', ''), S['kind']), font=M.font(fit(S['when'] + S['kind'], 44, 780)), fill=(255, 140, 90), anchor='lm')
            d.text((x0 + 40, 950), (S.get('lines') or [''])[0], font=M.font(fit((S.get('lines') or [''])[0], 40, 780)), fill=(200, 200, 210), anchor='lm')
        M.paste_char(im, t, W / 2 + 260, 1820, 640)
    else:
        M.glow_text(im, (W / 2, 420), 'oshinavi.jp', int(80 + 50 * M.ease(u / 0.5)), fill=M.WHITE, glow=M.WHITE)   # URLは光る白（memory）
        d.text((W / 2, 600), '推しのチケット発売日、見逃さない', font=M.font(56), fill=M.WHITE, anchor='mm', stroke_width=5, stroke_fill=(90, 0, 140))
        M.paste_char(im, t, W / 2, 1750, 950)
    if t > DUR - 0.6:
        im = Image.blend(im, Image.new('RGB', im.size, M.DEEP), min(1.0, (t - (DUR - 0.6)) / 0.6 * 0.85))
    return im


def board(S, path):
    shots = [1.6, 4.8, 7.8, 9.2]
    sw = 270; sh = int(sw * H / W)
    b = Image.new('RGB', (len(shots) * (sw + 12) + 12, sh + 24), (30, 30, 30))
    for i, tt in enumerate(shots):
        b.paste(render(tt, S).resize((sw, sh), Image.LANCZOS), (12 + i * (sw + 12), 12))
    b.save(path)
    print('絵コンテ', path)


def render_all(S):
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    out = S['out']
    os.makedirs(os.path.dirname(out), exist_ok=True)
    p = subprocess.Popen([ff, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
                          '-i', M.SONG, '-t', str(DUR), '-af', 'afade=t=out:st=%.1f:d=0.8' % (DUR - 0.8),
                          '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '23', '-c:a', 'aac', '-b:a', '128k',
                          '-movflags', '+faststart', '-shortest', out], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for i in range(int(DUR * FPS)):
        p.stdin.write(render(i / FPS, S).tobytes())
    p.stdin.close(); p.wait()
    print('動画', out, os.path.getsize(out) // 1024, 'KB')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('--board', action='store_true')
    ap.add_argument('--render', action='store_true')
    a = ap.parse_args()
    S = json.load(io.open(a.spec, encoding='utf-8'))
    if a.board:
        board(S, os.path.splitext(a.spec)[0] + '_board.png')
    if a.render:
        render_all(S)
