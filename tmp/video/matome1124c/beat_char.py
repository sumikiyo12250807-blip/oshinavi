# -*- coding: utf-8 -*-
# キャラを曲の拍に合わせて動かす（matome1101s/beat_char.py の第2版と同じ直し）
#   拍＝beats.json（beats_kick.py＝124.78BPM の格子をキックに4秒ごとに当て直した拍）
#   ・拍の直前 15% で素早く沈み、拍ちょうどで一番下（高さの 3%）、そのあと 0.22 拍の速さで戻る
#   ・2拍で左右に傾く（±2°）・傾きのいちばん端も拍ちょうど
#   ・大きさ（11/1 すちこ「キャラの大きさが全然変わっていない」）＝9ポーズ同じ倍率 SCALE
#     上のかぼちゃの列の下の端 185 ＋余白 60 ＝245 から、歌詞の塊（3行）のいちばん上の行の上の端 約905 −余白 60 ＝845 までの 600 に、
#     いちばん背の高い絵（p3 悪魔の玉座 936px）が沈み 3% 込みで入る＝高さ 582 ＝倍率 0.622（横いちばん長いソファ p8 1078px → 670）
#     縦の位置は、すき間のまん中（545）に絵のまん中をそろえる（寝そべり・ソファも上が空かない）。引数の bottom・h は使わない
#   tools/oshimade_mv.paste_char を置き換える（道具は書き換えない）
import bisect, glob, io, json, math
from PIL import Image
import oshimade_mv as M

B = json.load(io.open('C:/Users/user/oshinavi/tmp/video/matome1124c/beats.json'))['beats']
SINK, TILT = 0.03, 2.0
TOP, BOT = 110, 850   # 11/13 足もとを 880→850 に上げる（5行の歌詞の上の端 約 860 にかけない）
MAXH = max(Image.open(f).height for f in glob.glob('C:/Users/user/oshinavi/tmp/video/matome1124c/poses/[wmstab][1-9].png'))   # 11/11 パリコレの子   # 11/9 雨の子 r（シートの向き）・n（反転）   # 11/8 祭りの子 k（元の向き）・n（反転）
SCALE = (BOT - TOP) / (1 + SINK) / MAXH
MID = (TOP + BOT) / 2


def phase(t):
    """(拍の番号, 拍の中の位置 0〜1)"""
    i = bisect.bisect_right(B, t) - 1
    if i < 0:
        p = B[1] - B[0]
        return -1, 1 + (t - B[0]) / p
    nxt = B[i + 1] if i + 1 < len(B) else B[i] + (B[i] - B[i - 1])
    return i, (t - B[i]) / max(1e-6, nxt - B[i])


def paste_char(im, t, cx, bottom, h, tilt=True):
    name = M.CUR['pose']
    c = M.pose_img(name)
    i, p = phase(t)
    p = p % 1.0
    hh = int(c.height * SCALE)
    f = math.exp(-p / 0.22) + (((p - 0.85) / 0.15) ** 2 if p > 0.85 else 0.0)
    sink = SINK * hh * min(1.0, f)
    ang = TILT * math.cos(math.pi * (i + p)) if tilt else 0
    # 11/8 すちこ「おじぎなし」＝止める子なし／「おどってるみたいに頻繁に変えて」＝2拍ごとに替わる＝足元の高さと頭の横位置をそろえて、ポーズだけが切り替わって見えるように
    c2 = c.resize((max(1, int(c.width * SCALE)), hh), Image.LANCZOS).rotate(ang, resample=Image.BICUBIC, expand=True)
    base = FOOT                                          # 沈んでいない時のかかと＝全ポーズ同じ高さ
    ax = head_x(name) * SCALE                            # 頭のまん中（絵の左端から）
    x = int(cx - ax - (c2.width - c.width * SCALE) / 2 + M.CUR.get('dx', 0.0))
    if not M.CUR.get('dx'):                               # 11/9 横に広い絵（ベンチ・階段・窓）が画面の端で切れない＝内側へ寄せる
        x = max(10, min(M.W - 10 - c2.width, x))
    im.paste(c2, (x, int(base - hh - (c2.height - hh) / 2 + sink)), c2)


FOOT = BOT - SINK * MAXH * SCALE
_HX = {}


def head_x(name):
    """絵の上 35% の不透明な所の横のまん中＝頭の位置（太鼓・提灯を持つ子も頭で並ぶ）"""
    if name not in _HX:
        import numpy as np
        a = np.asarray(M.pose_img(name).convert('RGBA'))[:, :, 3]
        top = a[: max(1, int(a.shape[0] * 0.35))] > 40
        xs = np.where(top.any(axis=0))[0]
        w = top.sum(axis=0).astype(float)
        _HX[name] = float((w * np.arange(a.shape[1])).sum() / max(1.0, w.sum())) if len(xs) else a.shape[1] / 2
    return _HX[name]


M.paste_char = paste_char
