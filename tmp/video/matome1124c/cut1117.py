# -*- coding: utf-8 -*-
# 11/17 J-POP のちび姐さん9人（jpop_chibi_1117.png・背景透明）＝透明のまま切る（cut_alpha9.py sheet.png w）
#   → poses/w1〜w9（シートの向き）・m1〜m9（反転）・look_w*.png（元の絵と切り抜き〔緑の地〕を高さ 700 で横に並べる）・contact_poses.png
import io, os, subprocess, sys
from PIL import Image, ImageOps, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
P = D + 'poses/'
for f in os.listdir(P):
    os.remove(P + f)
r = subprocess.run([sys.executable, D + 'cut_alpha9.py', 'sheet.png', 'w'], capture_output=True, text=True, encoding='utf-8', errors='replace')
log = ['cut rc %d %s' % (r.returncode, r.stderr[-800:])]
log += io.open(D + 'cut9_w.txt', encoding='utf-8').read().splitlines()
src = Image.open(D + 'sheet.png').convert('RGBA')
boxes = {}
for l in log:
    if l.startswith('w') and 'シート上' in l:
        k = l.split()[0]
        boxes[k] = tuple(int(v) for v in l.split('シート上')[1].strip(' ()').split(','))
tiles = []
for k in range(1, 10):
    nm = 'w%d' % k
    im = Image.open(P + nm + '.png').convert('RGBA')
    ImageOps.mirror(im).save(P + 'm%d.png' % k)
    x0, y0, x1, y1 = boxes[nm]
    edge = [s for s, v in (('左', x0 <= 1), ('上', y0 <= 1), ('右', x1 >= src.width - 1), ('下', y1 >= src.height - 1)) if v]
    log.append('%s 絵の端に触れた %s' % (nm, ''.join(edge) or 'なし'))
    b = (max(0, x0 - 25), max(0, y0 - 25), min(src.width, x1 + 25), min(src.height, y1 + 25))
    o = Image.new('RGBA', (b[2] - b[0], b[3] - b[1]), (255, 255, 255, 255))
    o.alpha_composite(src.crop(b))
    th = 700
    k2 = th / o.height
    o = o.convert('RGB').resize((int(o.width * k2), th), Image.LANCZOS)
    g = Image.new('RGBA', o.size, (0, 150, 60, 255))
    c = im.resize((int(im.width * k2), int(im.height * k2)), Image.LANCZOS)
    g.alpha_composite(c, (int((x0 - b[0]) * k2), int((y0 - b[1]) * k2)))
    row = Image.new('RGB', (o.width * 2 + 20, th), (30, 30, 30))
    row.paste(o, (0, 0)); row.paste(g.convert('RGB'), (o.width + 20, 0))
    ImageDraw.Draw(row).text((8, 8), nm, fill=(255, 0, 0))
    row.save(D + 'look_w%d.png' % k)
    tiles.append(row)
io.open(D + 'cut1117.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
