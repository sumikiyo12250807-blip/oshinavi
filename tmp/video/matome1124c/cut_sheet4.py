# -*- coding: utf-8 -*-
# ドレス9着の切り抜き（matome1030c/cut_sheet3.py の市松模様の見分け方＋このシート用の箱）
#   このシートは3×3の升目にそろっていない（真ん中のラベンダーは横に広い・左下の白は列をはみ出す・段の境もずれる）
#   ＝3等分の列では切らず、1着ずつ手で決めた広めの箱を isnet-anime で抜く
#   市松模様（色みのない約252と約225の10px升目）は「2色が交互」で見分けて、抜いたあとに透明にする
#   箱の中の塊のうち、いちばん大きい塊と、その外接矩形の中にある塊だけ残す。箱の端に触れる小さい塊（隣の人のかけら）は捨てる
#   → poses/p1〜p9.png・poses/compare.png（元シートと並べる）・cut_sheet4.txt
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
sheet = Image.open(D + 'sheet.png').convert('RGB')
W, H = sheet.size
BOX = {1: (55, 0, 420, 448), 2: (440, 0, 820, 468), 3: (875, 0, 1195, 468),
       4: (90, 432, 378, 915), 5: (392, 458, 856, 872), 6: (880, 455, 1210, 918),
       7: (0, 855, 450, 1254), 8: (505, 838, 805, 1254), 9: (835, 890, 1254, 1254)}
_a = np.asarray(sheet).astype(int)
_neu = (_a.max(axis=2) - _a.min(axis=2) < 7) & (_a.sum(axis=2) > 3 * 200)
_lum = _a.sum(axis=2) / 3
_A = _neu & (_lum >= 239)
_B = _neu & (_lum >= 210) & (_lum < 239)
_fa = cv2.blur(_A.astype(np.float32), (25, 25))
_fb = cv2.blur(_B.astype(np.float32), (25, 25))
CHK = (_fa > 0.2) & (_fb > 0.2) & (_fa + _fb > 0.85)
CHK = (cv2.dilate(CHK.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0) & _neu
Image.fromarray((CHK * 255).astype(np.uint8)).save(D + 'poses_chk.png')
log = open(D + 'cut_sheet4.txt', 'w', encoding='utf-8')
S = 2


def mask_of(c):
    x = np.asarray(c.resize((1024, 1024), Image.LANCZOS)).astype(np.float32)
    x = x / max(x.max(), 1e-6)
    x = (x - np.array([0.485, 0.456, 0.406], dtype=np.float32))
    x = x.transpose(2, 0, 1)[None].astype(np.float32)
    p = sess.run(None, {inp: x})[0][:, 0]
    p = (p - p.min()) / max(p.max() - p.min(), 1e-6)
    return Image.fromarray((p[0] * 255).astype(np.uint8)).resize(c.size, Image.LANCZOS)


res = {}
for k, (x0, y0, x1, y1) in BOX.items():
    crop = sheet.crop((x0, y0, x1, y1)).resize(((x1 - x0) * S, (y1 - y0) * S), Image.LANCZOS)
    m = np.asarray(mask_of(crop))
    m = np.where(m < 40, 0, np.where(m > 200, 255, m)).astype(np.uint8)
    chk = cv2.resize(CHK[y0:y1, x0:x1].astype(np.uint8), crop.size, interpolation=cv2.INTER_NEAREST) > 0
    m = np.where(chk, 0, m).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats((m > 60).astype(np.uint8), 8)
    main = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    mb = st[main]
    hh, ww = m.shape
    keep = {main}
    for j in range(1, n):
        if j == main or st[j, cv2.CC_STAT_AREA] < st[main, cv2.CC_STAT_AREA] * 0.002:
            continue
        l, t, w, h = st[j, :4]
        touches = l <= 1 or t <= 1 or l + w >= ww - 1 or t + h >= hh - 1
        cx, cy = cen[j]
        inside = mb[0] <= cx <= mb[0] + mb[2] and mb[1] <= cy <= mb[1] + mb[3]
        if inside and not touches:
            keep.add(j)
    km = np.where(np.isin(lab, list(keep)), m, 0).astype(np.uint8)
    solid = (km > 60).astype(np.uint8)
    ff = np.pad(1 - solid, 1, constant_values=1).copy()
    fm = np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8)
    cv2.floodFill(ff, fm, (0, 0), 2)
    holes = (ff[1:-1, 1:-1] == 1)
    holes &= ~chk          # 市松模様が透けて見える穴（腕と体のすき間）は埋めない
    km = np.where(holes, 255, km).astype(np.uint8)
    inner = cv2.erode((solid | holes).astype(np.uint8), np.ones((17, 17), np.uint8))
    km = np.maximum(km, np.where(chk, 0, inner * 255)).astype(np.uint8)
    ys, xs = np.where(km > 60)
    bb = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    edge = [s for s, v in (('左', bb[0] <= 2), ('上', bb[1] <= 2), ('右', bb[2] >= ww - 2), ('下', bb[3] >= hh - 2)) if v]
    rgba = crop.convert('RGBA')
    rgba.putalpha(Image.fromarray(km))
    im = rgba.crop(bb)
    im.save(os.path.join(OUT, 'p%d.png' % k))
    res[k] = (im, (x0 + bb[0] / S, y0 + bb[1] / S, x0 + bb[2] / S, y0 + bb[3] / S))
    log.write('p%d 大きさ %s 塊 %d/%d 箱の端に触れる %s シート上 %s\n' % (k, im.size, len(keep), n - 1, ''.join(edge) or 'なし',
                                                          tuple(int(v) for v in res[k][1])))
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
