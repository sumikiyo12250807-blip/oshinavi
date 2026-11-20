# -*- coding: utf-8 -*-
# アイドル衣装9着の切り抜き（cut_sheet2 は上のコマの靴と下のコマの頭が光でつながって2人いっしょに抜けた）
#   ①シート全体を isnet-anime で抜いてマスクを作る（2倍で）
#   ②列（3等分）ごとに、マスクの横幅がいちばん細い高さ（＝靴と次の頭のくびれ）を上下の切れ目にする
#   ③列×切れ目の範囲で、いちばん大きな塊と、それにほぼ接する塊だけ残す
#   → poses/p1〜p9.png・poses/compare.png
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import onnxruntime as ort
import cv2
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
OUT = D + 'poses'
os.makedirs(OUT, exist_ok=True)
sess = ort.InferenceSession('C:/Users/user/oshinavi/tmp/video/models/isnet-anime.onnx', providers=['CPUExecutionProvider'])
inp = sess.get_inputs()[0].name
src = Image.open(D + 'sheet.png').convert('RGBA')
bg = Image.new('RGBA', src.size, (0, 0, 0, 255))
bg.alpha_composite(src)
sheet = bg.convert('RGB')
W, H = sheet.size
log = open(D + 'cut_sheet3.txt', 'w', encoding='utf-8')
S = 2
big = sheet.resize((W * S, H * S), Image.LANCZOS)


def mask_of(c):
    x = np.asarray(c.resize((1024, 1024), Image.LANCZOS)).astype(np.float32)
    x = x / max(x.max(), 1e-6)
    x = (x - np.array([0.485, 0.456, 0.406], dtype=np.float32))
    x = x.transpose(2, 0, 1)[None].astype(np.float32)
    p = sess.run(None, {inp: x})[0][:, 0]
    p = (p - p.min()) / max(p.max() - p.min(), 1e-6)
    return Image.fromarray((p[0] * 255).astype(np.uint8)).resize(c.size, Image.LANCZOS)


# 列ごとに抜く（列の幅だけの縦長を抜くほうが細部が出る）
res = {}
for c in range(3):
    x0, x1 = int(W * c / 3), int(W * (c + 1) / 3)
    col = big.crop((x0 * S, 0, x1 * S, H * S))
    m = np.asarray(mask_of(col))
    m = np.where(m < 40, 0, np.where(m > 200, 255, m)).astype(np.uint8)
    width = (m > 100).sum(axis=1)
    cuts = [0]
    for lo, hi in ((0.30, 0.42), (0.66, 0.77)):
        a, b = int(H * S * lo), int(H * S * hi)
        y = a + int(np.argmin(width[a:b]))
        cuts.append(y)
    cuts.append(H * S)
    # くびれの自動判定は靴の途中を切った＝つなぎ目を拡大して見たすき間の高さ（シートの座標）で切る（poses/junction.png）
    cuts = [0, [471, 472, 476][c] * S, [908, 870, 912][c] * S, H * S]   # p6・p7・p9 の頭に上の靴の底が細く残った3か所は 5px 下げた
    log.write('列%d 切れ目 %s 幅 %s\n' % (c, [v // S for v in cuts], [int(width[v]) for v in cuts[1:-1]]))
    # 横一直線で切ると、上の段の靴の底が下の段へ落ちる＝範囲を下へ 200 広げて靴の底まで入れ、
    #   上の端に触れている塊（＝上の段の靴のかけら）は捨てる。下の段の頭は別の塊で、体の外接矩形の外にあるので入らない
    for r in range(3):
        ya, yb = cuts[r], cuts[r + 1]
        sub = m[ya:yb].copy()
        n, lab, st, cen = cv2.connectedComponentsWithStats((sub > 60).astype(np.uint8), 8)
        own = [j for j in range(1, n) if not (r > 0 and st[j, cv2.CC_STAT_TOP] <= 1 and st[j, cv2.CC_STAT_TOP] + st[j, cv2.CC_STAT_HEIGHT] < (cuts[r + 1] - ya) * 0.3)]
        main = max(own, key=lambda j: st[j, cv2.CC_STAT_AREA])
        mb = st[main]
        ex = 0.05 * max(mb[2], mb[3])
        keep = {main}
        for j in range(1, n):
            if j != main and st[j, cv2.CC_STAT_AREA] >= st[main, cv2.CC_STAT_AREA] * 0.01:
                cx, cy = cen[j]
                if mb[0] - ex <= cx <= mb[0] + mb[2] + ex and mb[1] - ex <= cy <= mb[1] + mb[3] + ex:
                    keep.add(j)
        km = np.where(np.isin(lab, list(keep)), sub, 0).astype(np.uint8)
        # 目の光などを背景と間違えて抜いた中の穴を埋める（外から届かない所＝中）
        solid = (km > 60).astype(np.uint8)
        ff = np.pad(1 - solid, 1, constant_values=1).copy()
        fm = np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8)
        cv2.floodFill(ff, fm, (0, 0), 2)
        holes = (ff[1:-1, 1:-1] == 1)
        km = np.where(holes, 255, km).astype(np.uint8)
        # 半分透けた所（目の光）も埋める＝塗りつぶした形を 8px 内側へ縮めた所は全部不透明・ふちだけやわらかく残す
        inner = cv2.erode((solid | holes).astype(np.uint8), np.ones((17, 17), np.uint8))
        km = np.maximum(km, inner * 255).astype(np.uint8)
        ys, xs = np.where(km > 60)
        bb = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        rgba = col.crop((0, ya, col.width, yb)).convert('RGBA')
        rgba.putalpha(Image.fromarray(km))
        im = rgba.crop(bb)
        k = r * 3 + c + 1
        im.save(os.path.join(OUT, 'p%d.png' % k))
        edge = bb[1] <= 1 and r > 0 or bb[3] >= km.shape[0] - 1 and r < 2
        res[k] = (im, (x0 + bb[0] / S, (ya + bb[1]) / S, x0 + bb[2] / S, (ya + bb[3]) / S))
        log.write('p%d 大きさ %s 塊 %d 切れ目に触れる %s\n' % (k, im.size, len(keep), edge))
th = 520
rows = []
for k in range(1, 10):
    im, box = res[k]
    b = (max(0, int(box[0]) - 20), max(0, int(box[1]) - 20), min(W, int(box[2]) + 20), min(H, int(box[3]) + 20))
    o = sheet.crop(b)
    o = o.resize((int(o.width * th / o.height), th), Image.LANCZOS)
    g = Image.new('RGB', (int(im.width * th / im.height) + 40, th + 40), (0, 170, 60))
    r2 = im.resize((int(im.width * th / im.height), th), Image.LANCZOS)
    g.paste(r2, (20, 20), r2)
    g = g.resize((int(g.width * th / g.height), th))
    row = Image.new('RGB', (o.width + g.width + 30, th + 30), (30, 30, 30))
    row.paste(o, (0, 30)); row.paste(g, (o.width + 30, 30))
    ImageDraw.Draw(row).text((4, 4), 'p%d' % k, fill=(255, 255, 255))
    rows.append(row)
cw = max(r.width for r in rows)
out = Image.new('RGB', (3 * (cw + 10), 3 * (th + 40)), (30, 30, 30))
for i, r in enumerate(rows):
    out.paste(r, ((i % 3) * (cw + 10), (i // 3) * (th + 40)))
out.save(OUT + '/compare.png')
log.close()
