# -*- coding: utf-8 -*-
# 第3版の背景（2026-10-25 すちこ「いいんだけど、上の暗い空間が気になる」）＝第2版のペンライトの動画（bg_video.py）の上半分の真っ黒を無くす
#   ①動画のコマを 1.25 倍に拡大して下寄りに切り出す（光の帯 y680〜 が y370 から始まる）＝元のコマはもうぼかしてあるので粗さは目立たない
#   ②まだ足りない上の部分は、光の帯を上下反転して強くぼかし半分の明るさにした絵で埋める（天井に光が映っている感じ）
#   ③上に向かって紫〜青のグラデーションの光をうっすら screen で重ねる
#   ループとつなぎ目のクロスフェードは bg_video.py のまま（frame() を差し替える）
from PIL import Image, ImageChops, ImageFilter
import oshimade_mv as M
import bg_video as BV

K = 1.25
CW, CH = int(M.W / K), int(M.H / K)            # 864×1536 を切って 1080×1920 へ
X0, Y0 = (M.W - CW) // 2, M.H - CH
REF_H, REF_FROM = 620, 380                      # 反転して上に置く高さ・帯のどこから取るか（拡大後の y）
_grad = {}
_orig_frame = BV.frame
_c3 = {}


def grad():
    if 'g' not in _grad:
        g = Image.new('RGB', (1, M.H))
        for y in range(M.H):
            k = max(0.0, 1 - y / 1000) ** 1.6          # 上ほど強い・y1000 で 0
            a = y / 1000
            col = (int((70 + 40 * a) * k), int((30 + 30 * a) * k), int((170 - 30 * a) * k))   # 上＝青紫・下へ紫
            g.putpixel((0, y), col)
        _grad['g'] = g.resize((M.W, M.H))
        m = Image.new('L', (1, REF_H))
        for y in range(REF_H):
            m.putpixel((0, y), int(255 * min(1.0, (REF_H - y) / (REF_H * 0.55))))   # 上は不透明・下端へ溶かす
        _grad['m'] = m.resize((M.W, REF_H))
    return _grad['g'], _grad['m']


def make(f):
    g, m = grad()
    im = f.crop((X0, Y0, X0 + CW, Y0 + CH)).resize((M.W, M.H), Image.BICUBIC)
    band = im.crop((0, REF_FROM, M.W, REF_FROM + REF_H)).transpose(Image.FLIP_TOP_BOTTOM)
    band = band.resize((M.W // 4, REF_H // 4)).filter(ImageFilter.GaussianBlur(6)).resize((M.W, REF_H), Image.BILINEAR)
    band = Image.eval(band, lambda v: int(v * 0.55))
    top = im.crop((0, 0, M.W, REF_H))
    im.paste(ImageChops.lighter(top, band), (0, 0), m)
    return ImageChops.screen(im, g)


def frame(sec):
    i = max(1, min(BV.N, int(sec * BV.FPS) + 1))
    if i not in _c3:
        if len(_c3) > 6:
            _c3.clear()
        _c3[i] = make(_orig_frame(sec))
    return _c3[i]


BV.frame = frame
