# -*- coding: utf-8 -*-
"""横長の宿ボタン（img/btn_hotel_wide.png・すちこが ChatGPT で作った）を型に、字だけ差し替えた横長ボタンを作る（2026-11-24 朝）
すちこ「推しのうちわを作る　とかのボタンもホテルのボタンに似せて作れない？」
・型＝宿ボタンの枠と右の矢印はそのまま。真ん中（字と建物の絵）は、字の左の無地の列を横に敷き直して消す
・字＝白い太字（Noto Sans JP 900）＋黒っぽい縁取り＋下に少し影（宿ボタンの字に寄せる）
・右に小さな絵文字の代わりの絵は付けない（矢印だけ）＝見本を見てもらってから決める
使い方: python tmp/btn/wide_from_hotel_1124.py   → tmp/btn_tpl/wide_*.png と見本ページ tmp/btn_tpl/wide_preview.html"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
os.chdir('C:/Users/user/oshinavi')
SRC = 'img/btn_hotel_wide.png'
FONT = r'C:\Windows\Fonts\NotoSansJP-VF.ttf'
OUT = 'tmp/btn_tpl'
os.makedirs(OUT, exist_ok=True)
JOBS = [('uchiwa', '推しうちわを作る'), ('goods', '推し活グッズを見る'), ('operaglass', 'オペラグラスを見る'), ('earplug', 'ライブ用耳栓を見る'),
        ('kansen', '観戦グッズを見る'), ('cd', '予習する（最新CD）'), ('amazonmusic', 'Amazon Musicで聴く')]
base = Image.open(SRC).convert('RGBA')
W, H = base.size
px = base.load()
# 無地の列＝字の左（x=40〜55 の平均）を、x=40〜905 に敷く
X0, X1, Y0, Y1 = 34, 920, 10, H - 10   # 920＝右の矢印の箱（暗い色）が始まる手前
col = []
for y in range(H):
    rs = [px[x, y] for x in range(40, 56)]
    col.append(tuple(sum(c[i] for c in rs) // len(rs) for i in range(4)))
def make(text):
    im = base.copy()
    p = im.load()
    for x in range(X0, X1):
        for y in range(Y0, Y1):
            p[x, y] = col[y]
    try:
        f = ImageFont.truetype(FONT, 60)
        f.set_variation_by_axes([900])
    except Exception:
        f = ImageFont.truetype(r'C:\Windows\Fonts\HGSoeiKakugothicUB_X0213(04).ttc', 60)
    size = 60
    d = ImageDraw.Draw(im)
    while d.textlength(text, font=f) > (X1 - 60 - 70) and size > 36:
        size -= 2
        f = ImageFont.truetype(FONT, size)
        try:
            f.set_variation_by_axes([900])
        except Exception:
            pass
    tw = d.textlength(text, font=f)
    x = 70 + ((X1 - 40 - 70) - tw) / 2
    bb = d.textbbox((0, 0), text, font=f)
    y = H / 2 - (bb[1] + bb[3]) / 2
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((x + 2, y + 4), text, font=f, fill=(0, 0, 0, 190))
    sh = sh.filter(ImageFilter.GaussianBlur(2))
    im = Image.alpha_composite(im, sh)
    d = ImageDraw.Draw(im)
    d.text((x, y), text, font=f, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(10, 18, 50, 255))
    return im
rows = []
for name, text in JOBS:
    im = make(text)
    fn = '%s/wide_%s.png' % (OUT, name)
    im.convert('RGBA').quantize(256).save(fn, optimize=True)
    rows.append((name, text, os.path.basename(fn)))
    print(fn, os.path.getsize(fn))
