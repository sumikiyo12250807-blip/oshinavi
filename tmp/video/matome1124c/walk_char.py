# -*- coding: utf-8 -*-
# 11/13 すちこ「立ってる画像（2枚目）をメインに・颯爽と歩くところを続けて」＝歩く子（w＝シートの向き＝右向き／m＝反転＝左向き）を
#   着替えのたびに画面の外から歩いて入れ、上半分のまん中あたりをゆっくり進み、次の子に替わる時は歩いて出ていく
#   ・入る 1.3 秒（だんだんゆっくり）→ まん中を左右 ±8% ゆっくり進む → 替わる 0.6 秒前から 1.2 秒で出ていく（だんだん速く）
#   ・向きが変わる所だけ、次の子は 0.6 秒遅れて入る（出ていく子とすれ違ってぶつからない）
#   ・拍ごとに足もとが弾む（拍ちょうどで下・拍の間で上）・前後に ±1.5° 揺れる（2拍で1往復）
#   ・締め（最後の子）は入ってきたら まん中で足踏み
#   oshimade_mv.paste_char を置き換える（beat_char の後に import）。引数の cx・bottom・h は使わない
import bisect, glob, io, json, math
from PIL import Image
import oshimade_mv as M

D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
B = json.load(io.open(D + 'beats.json'))['beats']
TOP, BOT = 110, 850
MAXH = max(Image.open(f).height for f in glob.glob(D + 'poses/[wmstab][1-9].png'))
SCALE = (BOT - TOP) / 1.03 / MAXH
LIFT, TILT = 0.022, 1.5
ENT, EXA, EXB, DELAY = 1.3, 0.6, 0.6, 0.6
_S = {}
_IMG = {}


def install(S):
    _S['P'] = S['poses']
    _S['HOP'] = S.get('hop') or []


def img(name):
    if name not in _IMG:
        c = Image.open(D + 'poses/%s.png' % name).convert('RGBA')
        _IMG[name] = c.resize((max(1, int(c.width * SCALE)), max(1, int(c.height * SCALE))), Image.LANCZOS)
    return _IMG[name]


def phase(t):
    i = bisect.bisect_right(B, t) - 1
    if i < 0:
        p = B[1] - B[0]
        return -1, 1 + (t - B[0]) / p
    nxt = B[i + 1] if i + 1 < len(B) else B[i] + (B[i] - B[i - 1])
    return i, (t - B[i]) / max(1e-6, nxt - B[i])


def face(name):
    return 1 if name[0] in 'wsa' else -1


def walker(name):
    return name[0] in 'wmab'


def draw(im, name, xc, t, alpha=1.0, dy=0.0):
    i, p = phase(t)
    if name[0] in 'st' and (i // 2) % 2 == 1:   # 11/23 ビジュアル系＝2拍おきに同じ服の動いた絵（s→e・t→f）
        name = {'s': 'e', 't': 'f'}[name[0]] + name[1:]
    c = img(name)
    p = p % 1.0
    lift = -LIFT * c.height * math.sin(math.pi * p)          # 拍ちょうどで着地・拍の間で浮く
    if any(a <= t < b for a, b in _S.get('HOP', [])) and i % 4 == 0:
        lift *= 3.0   # 11/16 長い出番の後半＝1小節ごとに少し大きく跳ねる
    ang = TILT * math.cos(math.pi * (i + p)) * face(name)
    c2 = c.rotate(ang, resample=Image.BICUBIC, expand=True)
    if alpha < 1.0:
        c2 = c2.copy()
        c2.putalpha(c2.getchannel('A').point(lambda v: int(v * max(0.0, alpha))))
    x = int(xc - c2.width / 2)
    y = int(BOT - c.height - (c2.height - c.height) / 2 + lift + dy)
    im.paste(c2, (x, y), c2)


def paste_char(im, t, cx=None, bottom=None, h=None, tilt=True):
    P = _S['P']
    W = M.W
    n = len(P)
    for k in range(n):
        t0, name = P[k]
        t1 = P[k + 1][0] if k + 1 < n else None
        f = face(name)
        if not walker(name):   # 座る子＝まん中にふわっと現れ、替わる時はふわっと消える
            FI = 0.4
            tin = t0 + (0.5 if k and walker(P[k - 1][1]) else 0.0)
            if t < tin or (t1 is not None and t > t1 + 0.15):
                continue
            a = min(1.0, (t - tin) / FI)
            if t1 is not None and t > t1 - 0.25:
                a = min(a, (t1 + 0.15 - t) / 0.4)
            draw(im, name, W / 2, t, alpha=a, dy=-40 * (1 - min(1.0, (t - tin) / FI)) ** 2)
            continue
        same_prev = k and P[k - 1][1][1:] == name[1:]
        same_next = t1 is not None and k + 1 < n and P[k + 1][1][1:] == name[1:]
        tin = t0 + (DELAY if k and walker(P[k - 1][1]) and face(P[k - 1][1]) != f and not same_prev else 0.0)
        if same_next and t >= t1:
            continue
        if t < tin or (t1 is not None and t > t1 + EXB):
            continue
        w = img(name).width
        o0 = -w / 2 - 40 if f > 0 else W + w / 2 + 40
        o1 = W + w / 2 + 40 if f > 0 else -w / 2 - 40
        last = t1 is None
        A = W / 2 if last else W / 2 - f * W * 0.08
        Bx = W / 2 if last else W / 2 + f * W * 0.08
        if t < tin + ENT and not same_prev:
            u = (t - tin) / ENT
            x = o0 + (A - o0) * (1 - (1 - u) ** 2)
        elif last or same_next or t < t1 - EXA:
            span = max(0.1, (t1 - (0 if same_next else EXA)) - (tin + (0 if same_prev else ENT))) if not last else 1.0
            x = A + (Bx - A) * max(0.0, min(1.0, (t - tin - (0 if same_prev else ENT)) / span))
        else:
            u = (t - (t1 - EXA)) / (EXA + EXB)
            x = Bx + (o1 - Bx) * u * u
        draw(im, name, x, t)


M.paste_char = paste_char
