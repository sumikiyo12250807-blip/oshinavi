# -*- coding: utf-8 -*-
# 第2版の背景＝ペンライトの会場の動画（動画AC 134387）（matome1024j/bg_video.py の写し・フレームは matome1024j/bgf/*.jpg をそのまま読む）
#   2026-10-25 すちこ「やっぱりアップは見るに堪えないわ　背景はペンライトの動画にして小さく切り取っているのみたいに音楽に合わせて動かしてくれる」
#   曲（63.2秒）が動画（30.02秒）より長い分はループ。つなぎ目は 0.5 秒のクロスフェード。キラキラ・スポットライトは描かない
#   tools/oshimade_mv.background を差し替えるだけ（道具は書き換えない）
import os
from PIL import Image
import oshimade_mv as M

D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/bgf/'   # 11/1 かぼちゃの列 239279（bg_prep_1101.py）
FPS, L, XF = 30.0, 10.0, 0.6   # 11/17 紫のきらめき 7472（10.01 秒）   # 11/16 251638（20.02 秒）   # 11/12 雪の結晶 97366（30.04 秒）   # 11/6 青い光の粒 141688（10.03 秒）
N = len([f for f in os.listdir(D) if f.endswith('.jpg')])
P = L - XF
_cache = {}


def frame(sec):
    i = max(1, min(N, int(sec * FPS) + 1))
    if i not in _cache:
        if len(_cache) > 6:
            _cache.clear()
        _cache[i] = Image.open(D + '%04d.jpg' % i).convert('RGB')
    return _cache[i]


def background(t):
    if t < P:
        return frame(t).copy()
    u = (t - P) % P
    if u < XF:
        return Image.blend(frame(P + u), frame(u), u / XF)
    return frame(u).copy()


M.background = background
