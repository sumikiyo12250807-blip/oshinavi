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
KARA_SIZE, KARA_Y, KARA_W = 64, 1110, 1000   # 歌詞の文字の大きさ・位置・最大の幅（spec の kara_size / kara_y / kara_w で変える）
SONG_START = 0.0                          # 曲のどこから使うか（spec の song_start で変える）
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
    if S.get('poses'):                                # 🆕2026-10-04 歌詞の1行ごとに1ポーズ（ユーザー「動かしすぎ・歌詞に合わせて」）
        pt, pn, mv, nt = S['poses'][0][0], S['poses'][0][1], None, DUR
        for i, p in enumerate(S['poses']):
            if t >= p[0]:
                pt, pn = p[0], p[1]
                mv = p[2] if len(p) > 2 else None
                nt = S['poses'][i + 1][0] if i + 1 < len(S['poses']) else DUR
        M.CUR['pose'] = pn
        M.CUR['pop'] = t - pt
        # 🆕2026-10-04 ポーズごとの入り方（ユーザー「揺らすだけじゃなく、ゆっくり大きくしたり、縮めたり、横からスライドさせたり」）
        #   [時刻, ポーズ, 'zin'＝ゆっくり大きく / 'zout'＝ゆっくり小さく / 'sl'＝左から滑り込む / 'sr'＝右から]
        k = min(1.0, max(0.0, (t - pt) / max(0.1, nt - pt)))
        M.CUR['zoom'] = {'zin': 0.82 + 0.26 * k, 'zout': 1.14 - 0.24 * k}.get(mv, 1.0)
        e = M.ease((t - pt) / 0.6)
        M.CUR['dx'] = {'sl': -(1 - e) * W, 'sr': (1 - e) * W}.get(mv, 0.0)
        if mv in ('sl', 'sr'):
            M.CUR['pop'] = 9.0                        # 滑り込む時はポンと膨らませない
    else:
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
    elif name in HOWTO:
        howto(im, d, name, u, S)
        M.paste_char(im, t, W / 2 + 270, 1840, 620)
    elif name.startswith('list:'):                    # 🆕2026-10-06 まとめ動画＝発売時刻ごとの一覧（ユーザー「発売時間ごとに」）
        list_scene(im, name[5:], t, u, S)
        M.paste_char(im, t, W / 2, 1750, 900)
    elif name.startswith('shot:'):                    # 🆕2026-10-06 ユーザーのスクショで操作して見せる（押す所を光らせる・キャラが押す）
        shot_scene(im, name[5:], t, u, L, S)
    elif name == 'title':                             # 🆕まとめ動画の頭＝「明日 10/8(木) 発売 J-POP」
        M.glow_text(im, (W / 2, 330), S['when'], fit(S['when'], int(40 + 60 * M.ease(u / 0.8)), 1000))
        M.glow_text(im, (W / 2, 520), S['kind'], int(60 + 80 * M.ease((u - 0.4) / 0.8)), grad=(M.GOLD, M.PINK), glow=M.PINK)
        M.paste_char(im, t, W / 2, 1700, 950)
    else:
        M.glow_text(im, (W / 2, 420), 'oshinavi.jp', int(80 + 50 * M.ease(u / 0.5)), fill=M.WHITE, glow=M.WHITE)   # URLは光る白（memory）
        d.text((W / 2, 600), '推しのチケット発売日、見逃さない', font=M.font(56), fill=M.WHITE, anchor='mm', stroke_width=5, stroke_fill=(90, 0, 140))
        M.paste_char(im, t, W / 2, 1750, 950)
    if S.get('karaoke'):
        karaoke(im, t, S['karaoke'])
    lyr = None if S.get('karaoke') else lyric_at(t, S)
    if lyr:                                         # 🆕2026-10-04 1曲まるごとの版は歌詞を画面に出す（綴りは曲のタグの歌詞）
        d = ImageDraw.Draw(im)
        for j, ln in enumerate(lyr.split('\n')[:2]):
            sz = fit(ln, 60, 980)
            d.text((W / 2, 1110 + j * 84), ln, font=M.font(sz), fill=M.WHITE, anchor='mm', stroke_width=7, stroke_fill=(70, 0, 110))
    if t > DUR - 0.6:
        im = Image.blend(im, Image.new('RGB', im.size, M.DEEP), min(1.0, (t - (DUR - 0.6)) / 0.6 * 0.85))
    return im


# 🆕2026-10-05 使い方の場面（ユーザー「歌詞の中にオシナビの使い方とかもいれて、動画の画像にも使い方の説明とか入れてみて」
#   ／「みんなすぐいなくなっちゃうみたいだから」）＝本物の画面の切り抜きを大きく出し、押す所を点滅させて説明を出す。
#   切り抜きは tmp/video/howto/cut_*.png（tmp/x1005/x/shoot_howto.py・cut_howto.py）。枠は切り抜きの中の割合
HOWTO_DIR = 'tmp/video/howto'
HOWTO = {
    'how_search': ('search', (0.02, 0.08, 0.98, 0.92), 'STEP1 推しの名前を入れる', '検索窓に アーティスト名・イベント名'),
    'how_status': ('status', (0.283, 0.18, 0.49, 0.95), 'STEP2 今週発売を押す', '今週発売のチケットだけが並ぶ'),
    'how_area': ('area', (0.12, 0.04, 0.95, 0.97), 'STEP3 地方を選ぶ', 'あなたの街の公演だけにしぼれる'),
    'how_today': ('card_today', (0.045, 0.64, 0.21, 0.90), '本日発売は赤', '今日から買えるチケット'),
    'how_count': ('card_count', (0.045, 0.72, 0.34, 0.94), 'あと何日かひと目で', '発売開始まで あと◯日'),
}


def howto(im, d, name, u, S):
    key, box, title, cap = HOWTO[name]
    c = Image.open(os.path.join(HOWTO_DIR, 'cut_%s.png' % key)).convert('RGB')
    w = 1000
    r = w / c.width
    c = c.resize((w, int(c.height * r)), Image.LANCZOS)
    a = M.ease(u / 0.45)
    x0 = int((W - w) / 2 + (1 - a) * W)
    top = 470
    # 背景もOSHINAVIの画面なので、切り抜きが溶けないように上半分を暗く落とす
    reg = (0, 180, W, top + c.height + 150)
    im.paste(Image.blend(im.crop(reg), Image.new('RGB', (reg[2] - reg[0], reg[3] - reg[1]), (8, 4, 20)), 0.82), reg[:2])
    M.glow_text(im, (W / 2, 300), title, fit(title, 78, 1000), grad=(M.GOLD, M.PINK), glow=M.PINK)
    glow = Image.new('RGBA', (c.width + 60, c.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([20, 20, c.width + 40, c.height + 40], 24, outline=M.CYAN + (255,), width=10)
    from PIL import ImageFilter
    im.paste(glow.filter(ImageFilter.GaussianBlur(12)), (x0 - 30, top - 30), glow.filter(ImageFilter.GaussianBlur(12)))
    im.paste(c, (x0, top))
    d = ImageDraw.Draw(im)
    if name == 'how_search' and u > 0.5:                # 検索窓に主役の名前を打つ
        q = S.get('name', '')
        n = min(len(q), int((u - 0.5) / 0.12))
        h = c.height
        d.rectangle([x0 + 90, top + h * 0.28, x0 + w - 60, top + h * 0.72], fill=(14, 14, 18))
        d.text((x0 + 100, top + h / 2), q[:n] + ('|' if int(u * 3) % 2 == 0 else ''), font=M.font(fit(q, 54, 780)), fill=M.WHITE, anchor='lm')
    if u > 0.45:                                       # 押す所を点滅＋指の丸
        p = 0.5 + 0.5 * math.sin((u - 0.45) * 2 * math.pi * 1.6)
        bx0, by0, bx1, by1 = x0 + box[0] * w, top + box[1] * c.height, x0 + box[2] * w, top + box[3] * c.height
        col = tuple(int(M.GOLD[i] * p + M.PINK[i] * (1 - p)) for i in range(3))
        d.rounded_rectangle([bx0 - 8, by0 - 8, bx1 + 8, by1 + 8], 18, outline=col, width=9)
        cx, cy = (bx0 + bx1) / 2, by1 + 10
        rr = 26 + 12 * p
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=M.WHITE, width=6)
        d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=M.WHITE)
    yb = top + c.height + 70
    k = M.ease((u - 0.7) / 0.4)
    if k > 0:
        tw = d.textlength(cap, font=M.font(fit(cap, 56, 920)))
        d.rounded_rectangle([W / 2 - tw / 2 - 40, yb - 50, W / 2 + tw / 2 + 40, yb + 50], 30, fill=(14, 6, 34), outline=M.CYAN, width=5)
        d.text((W / 2, yb), cap, font=M.font(fit(cap, 56, 920)), fill=M.WHITE, anchor='mm')


ORIG_PASTE = None                                    # キャラを小さく右下に寄せる前の paste_char（押す場面ではバッジの横に立たせる）


def shot_scene(im, key, t, u, L, S):
    """S['shots'][key] = {'img': スクショ, 'crop': [x0,y0,x1,y1], 'boxes': [[x0,y0,x1,y1], …]（元画像の座標）, 'title': 上の見出し, 'tap': True}
    スクショを幅900で大きく出し、boxes を金とピンクで点滅させる。tap なら boxes を順にキャラが押す（指の丸が広がる）。"""
    from PIL import ImageFilter
    Q = S['shots'][key]
    src = Image.open(Q['img']).convert('RGB')
    cx0, cy0, cx1, cy1 = Q.get('crop') or (0, 0, src.width, src.height)
    c = src.crop((cx0, cy0, cx1, cy1))
    w = 900
    r = w / c.width
    c = c.resize((w, int(c.height * r)), Image.LANCZOS)
    a = M.ease(u / 0.45)
    x0, top = int((W - w) / 2 + (1 - a) * W), 330
    reg = (0, 180, W, top + c.height + 60)
    im.paste(Image.blend(im.crop(reg), Image.new('RGB', (reg[2], reg[3] - reg[1]), (8, 4, 20)), 0.82), reg[:2])
    if Q.get('title'):
        M.glow_text(im, (W / 2, 255), Q['title'], fit(Q['title'], 80, 1000), grad=(M.GOLD, M.PINK), glow=M.PINK)
    glow = Image.new('RGBA', (c.width + 60, c.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([20, 20, c.width + 40, c.height + 40], 24, outline=M.CYAN + (255,), width=10)
    g = glow.filter(ImageFilter.GaussianBlur(12))
    im.paste(g, (x0 - 30, top - 30), g)
    im.paste(c, (x0, top))
    boxes = [((bx0 - cx0) * r + x0, (by0 - cy0) * r + top, (bx1 - cx0) * r + x0, (by1 - cy0) * r + top) for bx0, by0, bx1, by1 in Q.get('boxes', [])]
    if not boxes or u < 0.45:
        M.paste_char(im, t, W / 2 + 270, 1840, 620)
        return
    d = ImageDraw.Draw(im)
    p = 0.5 + 0.5 * math.sin((u - 0.45) * 2 * math.pi * 1.6)
    col = tuple(int(M.GOLD[i] * p + M.PINK[i] * (1 - p)) for i in range(3))
    span = max(1.0, L)
    clean = [im.crop((int(b[0]), int(b[1]), int(b[2]), int(b[3]))) for b in boxes]   # 光を重ねる前の中身（文字が白く飛ばないように後で戻す）
    cur = min(len(boxes) - 1, int(u / (span / len(boxes)))) if Q.get('tap') else -1
    for i, (bx0, by0, bx1, by1) in enumerate(boxes):
        hot = (cur == i) or not Q.get('tap')
        lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).rounded_rectangle([bx0 - 18, by0 - 18, bx1 + 18, by1 + 18], 22, outline=col + (255,), width=26 if hot else 6)
        lg = lay.filter(ImageFilter.GaussianBlur(16 if hot else 8))
        im.paste(lg, (0, 0), lg)
        im.paste(lg, (0, 0), lg)                        # 2回重ねて強く光らせる（ユーザー「目立たせて」）
        reg = clean[i]
        s = 1.0 + 0.06 * p if hot else 1.0             # 光らせる所は中身を少し大きくして浮かせる（脈打つ）
        rw, rh2 = int(reg.width * s), int(reg.height * s)
        im.paste(reg.resize((rw, rh2), Image.LANCZOS), (int((bx0 + bx1 - rw) / 2), int((by0 + by1 - rh2) / 2)))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([bx0 - 10, by0 - 10, bx1 + 10, by1 + 10], 16, outline=col if hot else (120, 110, 150), width=8 if hot else 3)
    if Q.get('tap') and cur >= 0:
        bx0, by0, bx1, by1 = boxes[cur]
        k = (u % (span / len(boxes))) / (span / len(boxes))
        tx, ty = bx1 - 6, by1 + 4                     # 指はバッジの右下の角＝日付の文字を隠さない
        for j in range(2):                            # 押した所から丸が広がる
            rr = 14 + 46 * ((k * 2 + j * 0.5) % 1.0)
            al = 1 - ((k * 2 + j * 0.5) % 1.0)
            d.ellipse([tx - rr, ty - rr, tx + rr, ty + rr], outline=tuple(int(v * al) for v in M.WHITE), width=6)
        d.ellipse([tx - 12, ty - 12, tx + 12, ty + 12], fill=M.WHITE)
        M.CUR['pose'] = 'side_l'                      # 左を向いてバッジに手をのばす
        M.CUR['zoom'], M.CUR['dx'] = 1.0, 0.0
        (ORIG_PASTE or M.paste_char)(im, t, bx1 + 185, by1 + 250, 400)   # 小さめに・バッジの右に立って手をのばす（歌詞にかからない高さ）
    else:
        M.paste_char(im, t, W / 2 + 270, 1840, 620)


def list_scene(im, key, t, u, S):
    """発売時刻ごとの一覧。S['blocks'][key] = {'title': '朝 10:00 発売', 'rows': [[名前, 県, 先行なら'先行', 読み始めの時刻], …]}
    歌っている行を金の枠で光らせる（読み上げと画面を合わせる）。"""
    B = S['blocks'][key]
    d = ImageDraw.Draw(im)
    reg = (0, 170, W, 1080)                           # 背景の画面と文字が混ざらないように暗く落とす
    im.paste(Image.blend(im.crop(reg), Image.new('RGB', (reg[2], reg[3] - reg[1]), (8, 4, 20)), 0.78), reg[:2])
    M.glow_text(im, (W / 2, 260), B['title'], fit(B['title'], 92, 1000), grad=(M.GOLD, M.PINK), glow=M.PINK)
    rows = B['rows']
    rh = min(130, int(700 / max(1, len(rows))))
    y = 400
    for i, r in enumerate(rows):
        name, pref, tag, rt = r[0], r[1], r[2], r[3]
        a = M.ease((u - 0.15 * i) / 0.35)
        if a <= 0:
            continue
        x = W / 2 + (1 - a) * 500
        on = rt <= t < (rows[i + 1][3] if i + 1 < len(rows) else 1e9)
        d.rounded_rectangle([x - 490, y, x + 490, y + rh - 14], 22, fill=(40, 20, 60) if on else (14, 6, 34), outline=M.GOLD if on else M.CYAN, width=7 if on else 4)
        nsz = fit(name, min(54, int(rh * 0.42)), 600)
        d.text((x - 460, y + (rh - 14) / 2), name, font=M.font(nsz), fill=M.GOLD if on else M.WHITE, anchor='lm')
        right = pref + ('  先行' if tag else '')
        d.text((x + 460, y + (rh - 14) / 2), right, font=M.font(fit(right, min(44, int(rh * 0.34)), 330)), fill=(255, 140, 90) if tag else (210, 210, 225), anchor='rm')
        y += rh


def karaoke(im, t, segs):
    """歌詞を曲に合わせて1文字ずつ色でなぞる。segs = [{start, end, lines:[行,…], times:[文字ごとの時刻]}]（改行・空白を除いた文字順）"""
    seg = None
    for s in segs:
        if s['start'] - 0.3 <= t < s['end']:
            seg = s
    if not seg:
        return
    d = ImageDraw.Draw(im)
    k = 0
    for j, ln in enumerate(seg['lines'][:2]):
        sz = fit(ln, KARA_SIZE, KARA_W)
        f = M.font(sz)
        y = KARA_Y + j * int(KARA_SIZE * 1.4)
        x = W / 2 - d.textlength(ln, font=f) / 2
        for ch in ln:
            w = d.textlength(ch, font=f)
            if ch.strip():
                done = t >= seg['times'][k]
                k += 1
                col = M.GOLD if done else M.WHITE
                d.text((x, y), ch, font=f, fill=col, anchor='lm', stroke_width=max(7, sz // 9), stroke_fill=(150, 0, 110) if done else (70, 0, 110))
            x += w


def lyric_at(t, S):
    cur = None
    for tt, txt in S.get('lyrics') or []:
        if t >= tt:
            cur = txt
    return cur


def board(S, path):
    shots = S.get('board_shots') or [1.6, 4.8, 7.8, 9.2]
    sw = 270; sh = int(sw * H / W)
    b = Image.new('RGB', (len(shots) * (sw + 12) + 12, sh + 24), (30, 30, 30))
    for i, tt in enumerate(shots):
        b.paste(render(tt, S).resize((sw, sh), Image.LANCZOS), (12 + i * (sw + 12), 12))
    b.save(path)
    print('絵コンテ', path)
    for i, tt in enumerate(shots):                    # 🆕1コマずつ（幅540）も残す＝試し見のページで携帯でも読める
        render(tt, S).resize((540, int(540 * H / W)), Image.LANCZOS).save(os.path.splitext(path)[0] + '_%02d.png' % i)


def render_all(S):
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    out = S['out']
    os.makedirs(os.path.dirname(out), exist_ok=True)
    p = subprocess.Popen([ff, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
                          '-ss', str(SONG_START), '-i', M.SONG, '-t', str(DUR), '-af', AFADE,
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
    # 🆕2026-10-04 曲とキャラを spec で差し替える（無ければ『推しまで教えて』＋2026-09-29のキャラ）
    if S.get('song'):
        M.SONG = S['song']
    if S.get('posedir'):
        M.POSEDIR = S['posedir']; M._pose.clear()
    if S.get('song_start'):
        SONG_START = float(S['song_start'])
    if S.get('scenes'):                               # 🆕1曲まるごと（ユーザー「１曲全部作って」2026-10-04）＝場面の割りと長さを spec で
        SCENES = [tuple(x) for x in S['scenes']]
    if S.get('dur'):
        DUR = float(S['dur'])
    if S.get('site_bg'):                              # 背景を本物のOSHINAVIの画面に（キラキラはその上に重ねる）
        M.SITE_BG = S['site_bg']
    if S.get('beat'):                                 # 曲のテンポ（1拍の秒数）＝弾みを曲に合わせる
        M.BEAT = BEAT = float(S['beat'])
    if S.get('calm'):                                 # 揺れを小さく（ユーザー「動かしすぎかも」2026-10-04）
        M.BOUNCE, M.TILT, M.CLOSE_H = 6, 1.0, 640
    # 🆕2026-10-05 音の入りと終わり（ユーザー「2曲目が中途半端で始まって、半端に終わる感じ　フェイドアウトうまく入れると聞きやすい」）
    #   spec の fade_in（秒・既定0）と fade_out（秒・既定0.8）。切る位置は曲の静かな所（loudness.py で測る）
    # 🆕2026-10-06 まとめ動画（ユーザー「歌詞の文字を大きめでカラオケみたいに」「キャラは小さめにね」）
    KARA_SIZE, KARA_Y, KARA_W = int(S.get('kara_size', KARA_SIZE)), int(S.get('kara_y', KARA_Y)), int(S.get('kara_w', KARA_W))
    if S.get('char_scale'):                           # キャラの高さを何倍にするか＋置く場所（右下の隅）
        _pc, _cs, _cp = M.paste_char, float(S['char_scale']), S.get('char_pos')
        def _small(im, t, cx, bottom, h, tilt=True):
            if _cp:
                cx, bottom = _cp
            return _pc(im, t, cx, bottom, h * _cs, tilt)
        M.paste_char = _small
        ORIG_PASTE = _pc
    fi, fo = float(S.get('fade_in', 0)), float(S.get('fade_out', 0.8))
    AFADE = ('afade=t=in:st=0:d=%.2f,' % fi if fi > 0 else '') + 'afade=t=out:st=%.2f:d=%.2f' % (DUR - fo, fo)
    if a.board:
        board(S, os.path.splitext(a.spec)[0] + '_board.png')
    if a.render:
        render_all(S)
