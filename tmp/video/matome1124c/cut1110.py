# -*- coding: utf-8 -*-
# 11/10 九つの50年代レトロ・ガールズ（1536×1024・3×3・白地＝市松なし）の切り抜き（cut_rain.py の形を白地に合わせた）
#   ①地＝「外の縁につながった白」だけ（白い服・白いフリル・白い手袋の内側は地にしない＝線で囲まれている）
#   ②isnet-anime（2倍）で確信の高い所（>200）は地の白の中でも残す（線が途切れた白い服のすそ）
#   ③上下の段の子（r1 の靴と r4 の髪・r2 のすそと r5 の手・r5 の靴と r8 のリボン・r3 の車と r6 のベレー）は
#     各マスの芯を種に watershed で分ける ④いちばん大きい塊＋箱の中のかけら（落ち葉など）＋穴埋め
#   → poses/r1〜r9.png・poses/compare.png・cut1110.txt
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import onnxruntime as ort
import cv2
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
OUT = D + 'poses'
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    os.remove(os.path.join(OUT, f))
sess = ort.InferenceSession('C:/Users/user/oshinavi/tmp/video/models/isnet-anime.onnx', providers=['CPUExecutionProvider'])
inp = sess.get_inputs()[0].name
sheet = Image.open(D + 'sheet.png').convert('RGB')
W, H = sheet.size
S = 2
BOX = {1: (120, 0, 445, 352), 2: (535, 0, 870, 352), 3: (1000, 0, 1436, 352),
       4: (70, 326, 440, 715), 5: (550, 326, 905, 698), 6: (1005, 340, 1415, 700),
       7: (30, 712, 520, 1024), 8: (545, 672, 935, 1024), 9: (1040, 672, 1425, 1024)}
_a = np.asarray(sheet).astype(int)
_neu = (_a.max(axis=2) - _a.min(axis=2) < 10)
_lum = _a.sum(axis=2) / 3
WH = (_neu & (_lum >= 236)).astype(np.uint8)
n0, l0 = cv2.connectedComponents(WH, connectivity=4)
edge_labels = set(np.unique(np.concatenate([l0[0], l0[-1], l0[:, 0], l0[:, -1]]))) - {0}
BG = np.isin(l0, list(edge_labels))                 # 外の縁につながった白＝地
big = sheet.resize((W * S, H * S), Image.LANCZOS)
BG2 = cv2.resize(BG.astype(np.uint8), big.size, interpolation=cv2.INTER_NEAREST) > 0
log = open(D + 'cut1110.txt', 'w', encoding='utf-8')
log.write('地の白の塊 %d（縁につながる %d）\n' % (n0 - 1, len(edge_labels)))


def mask_of(c):
    x = np.asarray(c.resize((1024, 1024), Image.LANCZOS)).astype(np.float32)
    x = x / max(x.max(), 1e-6)
    x = (x - np.array([0.485, 0.456, 0.406], dtype=np.float32))
    x = x.transpose(2, 0, 1)[None].astype(np.float32)
    p = sess.run(None, {inp: x})[0][:, 0]
    p = (p - p.min()) / max(p.max() - p.min(), 1e-6)
    return Image.fromarray((p[0] * 255).astype(np.uint8)).resize(c.size, Image.LANCZOS)


ISN = np.zeros((H * S, W * S), np.uint8)
for k, (x0, y0, x1, y1) in BOX.items():
    crop = big.crop((x0 * S, y0 * S, x1 * S, y1 * S))
    m = np.asarray(mask_of(crop))
    ISN[y0 * S:y1 * S, x0 * S:x1 * S] = np.maximum(ISN[y0 * S:y1 * S, x0 * S:x1 * S], m)
ALPHA = np.where(~BG2, 255, np.where(ISN > 200, 255, 0)).astype(np.uint8)
FG = ALPHA > 60
mk = np.zeros(FG.shape, np.int32)
for k, (x0, y0, x1, y1) in BOX.items():
    w, h = x1 - x0, y1 - y0
    a, b, c, d = int((x0 + w * 0.25) * S), int((y0 + h * 0.25) * S), int((x1 - w * 0.25) * S), int((y1 - h * 0.25) * S)
    core = np.zeros(FG.shape, bool)
    core[b:d, a:c] = True
    mk[core & FG] = k
img = cv2.cvtColor(np.asarray(big), cv2.COLOR_RGB2BGR)
res = {}
for k, (x0, y0, x1, y1) in BOX.items():
    sub = mk[y0 * S:y1 * S, x0 * S:x1 * S].copy()
    # 第2版：地に「99」の種を置くと、芯（箱のまん中 50%）の外の髪・マイク・レコードを地が取った＝種は人の芯だけ（cut_rain と同じ）
    lw = cv2.watershed(np.ascontiguousarray(img[y0 * S:y1 * S, x0 * S:x1 * S]), sub)
    mine = np.zeros(FG.shape, bool)
    mine[y0 * S:y1 * S, x0 * S:x1 * S] = (lw == k)
    mine = cv2.dilate(mine.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    km = np.where(mine, ALPHA, 0).astype(np.uint8)
    if k == 6:   # 第2版：上の段 r3 のハイヒールのかかと（シートの y 352 まで）が r6 のベレーの上に残った＝上の帯を落とす
        #   第3版：帯ごと落とすとベレーのてっぺん（y 336〜）も消えた＝靴（x 1195〜・y 350 まで）と、ベレーに重なるタイヤの暗い所（x 1088〜1160・y 345 まで）だけ落とす
        km[340 * S:350 * S, 1195 * S:x1 * S] = 0
        _dk = (_lum[340:345, 1088:1160] < 120)
        _dk2 = cv2.resize(_dk.astype(np.uint8), (72 * S, 5 * S), interpolation=cv2.INTER_NEAREST) > 0
        km[340 * S:345 * S, 1088 * S:1160 * S][_dk2] = 0
    n, lab, st, cen = cv2.connectedComponentsWithStats((km > 60).astype(np.uint8), 8)
    main = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    mx0, my0, mw, mh = st[main, :4]
    keep = [main] + [j for j in range(1, n) if j != main and st[j, cv2.CC_STAT_AREA] > 120
                     and mx0 - 40 <= cen[j][0] <= mx0 + mw + 40 and my0 <= cen[j][1] <= my0 + mh]
    km = np.where(np.isin(lab, keep), km, 0).astype(np.uint8)
    solid = (km > 60).astype(np.uint8)
    ff = np.pad(1 - solid, 1, constant_values=1).copy()
    fm = np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8)
    cv2.floodFill(ff, fm, (0, 0), 2)
    enc = (ff[1:-1, 1:-1] == 1)
    km = np.where(enc & ~BG2, 255, km).astype(np.uint8)       # 囲まれた穴で地でない所を埋める
    # 縁の白いにじみを 1px 削って、なめらかに
    km = cv2.erode(km, np.ones((3, 3), np.uint8))
    km = cv2.GaussianBlur(km, (3, 3), 0)
    ys, xs = np.where(km > 60)
    bb = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    edge = []
    if bb[0] <= x0 * S + 2 and x0 > 0: edge.append('左')
    if bb[1] <= y0 * S + 2 and y0 > 0: edge.append('上')
    if bb[2] >= x1 * S - 2 and x1 < W: edge.append('右')
    if bb[3] >= y1 * S - 2 and y1 < H: edge.append('下')
    rgba = big.convert('RGBA')
    rgba.putalpha(Image.fromarray(km))
    im = rgba.crop(bb)
    im.save(os.path.join(OUT, 'r%d.png' % k))
    res[k] = (im, tuple(v / S for v in bb))
    log.write('r%d 大きさ %s 塊 %d シート上 %s 箱の端に触れた %s\n' % (k, im.size, len(keep), tuple(int(v) for v in res[k][1]), edge or 'なし'))
th = 520
rows = []
for k in range(1, 10):
    im, box = res[k]
    b = (max(0, int(box[0]) - 20), max(0, int(box[1]) - 20), min(W, int(box[2]) + 20), min(H, int(box[3]) + 20))
    o = sheet.crop(b)
    o = o.resize((int(o.width * th / o.height), th), Image.LANCZOS)
    g = Image.new('RGB', (int(im.width * th / im.height) + 40, th + 40), (20, 20, 50))
    r2 = im.resize((int(im.width * th / im.height), th), Image.LANCZOS)
    g.paste(r2, (20, 20), r2)
    g = g.resize((int(g.width * th / g.height), th))
    row = Image.new('RGB', (o.width + g.width + 30, th + 30), (30, 30, 30))
    row.paste(o, (0, 30)); row.paste(g, (o.width + 30, 30))
    ImageDraw.Draw(row).text((4, 4), 'r%d' % k, fill=(255, 255, 255))
    rows.append(row)
cw = max(r.width for r in rows)
out = Image.new('RGB', (3 * (cw + 10), 3 * (th + 40)), (30, 30, 30))
for i, r in enumerate(rows):
    out.paste(r, ((i % 3) * (cw + 10), (i // 3) * (th + 40)))
out.save(OUT + '/compare.png')
log.close()
