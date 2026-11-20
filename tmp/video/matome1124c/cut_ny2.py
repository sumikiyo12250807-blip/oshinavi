# -*- coding: utf-8 -*-
# 11/9 主役：冬の服のシート2枚（1536×1024・3×3・地は白と薄い灰の市松＝透明ではない）の切り抜き
#   matome1109o/cut_rain.py の写し：①1人ずつ広めの箱を isnet-anime で抜き（2倍）・市松の所は落とす
#   ②箱の中の芯を種に watershed ③いちばん大きい塊＋近くのかけら＋中の穴埋め
#   小物（街灯・ベンチ・雪だるま・猫・ランタン・本・買い物袋・マグ）も人の一部として残す（FULL＝箱の中の色のある所を全部前景に）
#   python cut_winter.py a|b → poses/w{a|b}1〜9.png・poses/compare_{a|b}.png・cut_winter_{a|b}.txt
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import onnxruntime as ort
import cv2
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
K = 'w'
OUT = D + 'poses'
os.makedirs(OUT, exist_ok=True)
sess = ort.InferenceSession('C:/Users/user/oshinavi/tmp/video/models/isnet-anime.onnx', providers=['CPUExecutionProvider'])
inp = sess.get_inputs()[0].name
sheet = Image.open(D + 'sheet2.png').convert('RGB')
W, H = sheet.size
S = 2
BOXES = {   # 11/10 boxes2.py：段の切れ目 481・上の列 302/618/922/1224・下の列 364/692/1102（となりと少し重ねる＝watershed で分ける）
    'w': {1: (0, 0, 318, 482), 2: (288, 0, 635, 482), 3: (600, 0, 964, 482), 4: (905, 0, 1268, 482), 5: (1208, 0, 1536, 482),
          6: (0, 482, 382, 1024), 7: (348, 482, 708, 1024), 8: (676, 482, 1120, 1024), 9: (1086, 482, 1536, 1024)},
}
FULLS = {'w': (1, 2, 3, 4, 5, 6, 7, 8, 9)}
FILLALL = {'w': ()}
FORCE = {}
DROP = {'w': {3: [(918, 55, 964, 150), (886, 78, 918, 132)]}}   # cw3 の顔の右の紫の点（cw4 の髪のかけら）
NETBOX = {5: [(1385, 40, 1505, 185)], 4: [(1085, 45, 1210, 175), (1140, 385, 1268, 482)], 1: [(0, 370, 318, 482)], 3: [(640, 375, 965, 472), (780, 30, 884, 190)]}   # 11/10 cw3 白いスニーカー（白い地と同じ色で消えた）・顔の右
FORCE = {}
NOHOLE = {}
DROP = {}
BOX = BOXES[K]
FULL = FULLS[K]
_a = np.asarray(sheet).astype(int)
_neu = (_a.max(axis=2) - _a.min(axis=2) < 8)
_lum = _a.sum(axis=2) / 3
CHK = _neu & (_lum >= 238)
big = sheet.resize((W * S, H * S), Image.LANCZOS)
CHK2 = cv2.resize(CHK.astype(np.uint8), big.size, interpolation=cv2.INTER_NEAREST) > 0
log = open(D + 'cut_ny2.txt', 'w', encoding='utf-8')


def mask_of(c):
    x = np.asarray(c.resize((1024, 1024), Image.LANCZOS)).astype(np.float32)
    x = x / max(x.max(), 1e-6)
    x = (x - np.array([0.485, 0.456, 0.406], dtype=np.float32))
    x = x.transpose(2, 0, 1)[None].astype(np.float32)
    p = sess.run(None, {inp: x})[0][:, 0]
    p = (p - p.min()) / max(p.max() - p.min(), 1e-6)
    return Image.fromarray((p[0] * 255).astype(np.uint8)).resize(c.size, Image.LANCZOS)


ALPHA = np.zeros((H * S, W * S), np.uint8)
for k, (x0, y0, x1, y1) in BOX.items():
    crop = big.crop((x0 * S, y0 * S, x1 * S, y1 * S))
    m = np.asarray(mask_of(crop))
    m = np.where(m < 40, 0, np.where(m > 200, 255, m)).astype(np.uint8)
    ALPHA[y0 * S:y1 * S, x0 * S:x1 * S] = np.maximum(ALPHA[y0 * S:y1 * S, x0 * S:x1 * S], m)
NET = ALPHA.copy()   # isnet だけの濃さ（白い毛皮・白いニット帽は市松と同じ白＝isnet が強く人と言う所は残す）
SOLID = cv2.resize(((~CHK) & ((_lum < 225) | (_a.max(axis=2) - _a.min(axis=2) > 25))).astype(np.uint8), big.size, interpolation=cv2.INTER_NEAREST)
SOLID = cv2.morphologyEx(SOLID, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
near = cv2.dilate((ALPHA > 100).astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
for k in FULL:
    x0, y0, x1, y1 = BOX[k]
    near[y0 * S:y1 * S, x0 * S:x1 * S] = True
ALPHA = np.where(near & (SOLID > 0), np.maximum(ALPHA, 230), ALPHA).astype(np.uint8)
ALPHA = np.where(CHK2 & (NET < 200), 0, ALPHA).astype(np.uint8)
FG = ALPHA > 60
mk = np.zeros(FG.shape, np.int32)
for k, (x0, y0, x1, y1) in BOX.items():
    w, h = x1 - x0, y1 - y0
    a, b, c, d = int((x0 + w * 0.25) * S), int((y0 + h * 0.25) * S), int((x1 - w * 0.25) * S), int((y1 - h * 0.25) * S)
    core = np.zeros(FG.shape, bool)
    core[b:d, a:c] = True
    mk[core & FG] = k
img = cv2.cvtColor(np.asarray(big), cv2.COLOR_RGB2BGR)
_NEU2 = cv2.resize(_neu.astype(np.uint8), big.size, interpolation=cv2.INTER_NEAREST) > 0
_LUM2 = cv2.resize(_lum.astype(np.float32), big.size, interpolation=cv2.INTER_NEAREST)
res = {}
for k, (x0, y0, x1, y1) in BOX.items():
    # 11/10 となりの子の靴と髪が重なる（cb6 の靴と cb9 のサングラス・cb5 の靴と cb8 の帽子）＝箱を 40px 広げ、
    #   となりの箱のうち自分の箱の外にある前景を「となりの子」の種にして一緒に watershed（重なった所は形の境目で分かれる）
    ex0, ey0, ex1, ey1 = max(0, x0 - 40), max(0, y0 - 40), min(W, x1 + 40), min(H, y1 + 40)
    mk2 = np.zeros(FG.shape, np.int32)
    mk2[mk == k] = k
    inme = np.zeros(FG.shape, bool); inme[y0 * S:y1 * S, x0 * S:x1 * S] = True
    for j, (a0, b0, a1, b1) in BOX.items():
        if j == k:
            continue
        inj = np.zeros(FG.shape, bool); inj[b0 * S:b1 * S, a0 * S:a1 * S] = True
        mk2[inj & ~inme & FG] = j
    sub = mk2[ey0 * S:ey1 * S, ex0 * S:ex1 * S].copy()
    lw = cv2.watershed(np.ascontiguousarray(img[ey0 * S:ey1 * S, ex0 * S:ex1 * S]), sub)
    mine = np.zeros(FG.shape, bool)
    mine[ey0 * S:ey1 * S, ex0 * S:ex1 * S] = (lw == k)
    mine &= inme
    mine = cv2.dilate(mine.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    km = np.where(mine, ALPHA, 0).astype(np.uint8)
    op = cv2.morphologyEx((km > 60).astype(np.uint8), cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    n0, l0, s0, _ = cv2.connectedComponentsWithStats(op, 8)
    if n0 > 1:
        big0 = (l0 == 1 + int(np.argmax(s0[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
        km = np.where(cv2.dilate(big0, np.ones((13, 13), np.uint8)) > 0, km, 0).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats((km > 60).astype(np.uint8), 8)
    main = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    keep = [main] + [j for j in range(1, n) if j != main and st[j, cv2.CC_STAT_AREA] > st[main, cv2.CC_STAT_AREA] * 0.004
                     and st[main, 0] <= cen[j][0] <= st[main, 0] + st[main, 2] and st[main, 1] <= cen[j][1] <= st[main, 1] + st[main, 3]]
    km = np.where(np.isin(lab, keep), km, 0).astype(np.uint8)
    for fx0, fy0, fx1, fy1 in FORCE.get(K, {}).get(k, []):   # 消えた小物（wa4 の街灯）＝その範囲の色のある所を足す
        rr = np.zeros(km.shape, bool); rr[fy0 * S:fy1 * S, fx0 * S:fx1 * S] = True
        km = np.where(rr & (SOLID > 0), np.maximum(km, 230), km).astype(np.uint8)
    for fx0, fy0, fx1, fy1 in DROP.get(K, {}).get(k, []):   # 下の段の子のかけら（wa6 の足もとのベレー帽）
        km[fy0 * S:fy1 * S, fx0 * S:fx1 * S] = 0
    for fx0, fy0, fx1, fy1 in NETBOX.get(k, []):   # 11/10 cn5 の顔の右（明るい肌が白い地と間違えて抜けた）＝その範囲は isnet の濃さを使う
        rr = np.zeros(km.shape, bool); rr[fy0 * S:fy1 * S, fx0 * S:fx1 * S] = True
        km = np.where(rr, np.maximum(km, NET), km).astype(np.uint8)
    solid = (km > 60).astype(np.uint8)
    ff = np.pad(1 - solid, 1, constant_values=1).copy()
    fm = np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8)
    cv2.floodFill(ff, fm, (0, 0), 2)
    enc = (ff[1:-1, 1:-1] == 1).astype(np.uint8)
    nh, lh, sh, _ = cv2.connectedComponentsWithStats(enc, 4)
    small = np.isin(lh, [j for j in range(1, nh) if sh[j, 4] < 9000])
    holes = (enc > 0) & (small | ~CHK2)
    for fx0, fy0, fx1, fy1 in NOHOLE.get(k, []):   # 11/10 cn8 のハートの中は透けたまま（穴埋めしない）
        rr = np.zeros(holes.shape, bool); rr[fy0 * S:fy1 * S, fx0 * S:fx1 * S] = True
        holes &= ~rr
    if k in FILLALL.get(K, ()):   # 雪だるまの白い胴・帽子の白いぼんぼり＝市松と同じ白で大きな穴になる＝囲まれた穴は全部埋める
        holes = enc > 0
    km = np.where(holes, 255, km).astype(np.uint8)
    inner = cv2.erode((solid | holes).astype(np.uint8), np.ones((17, 17), np.uint8))
    km = np.maximum(km, np.where(CHK2, 0, inner * 255)).astype(np.uint8)
    for _ in range(2):
        core_ = cv2.erode((km > 60).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        ring = (km > 0) & ~core_
        km = np.where(ring & _NEU2 & (_LUM2 >= 232), 0, km).astype(np.uint8)
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
    im.save(os.path.join(OUT, 'c%s%d.png' % (K, k)))
    res[k] = (im, tuple(v / S for v in bb))
    log.write('c%s%d 大きさ %s 塊 %d シート上 %s 箱の端に触れた %s\n' % (K, k, im.size, len(keep), tuple(int(v) for v in res[k][1]), edge or 'なし'))
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
    ImageDraw.Draw(row).text((4, 4), 'c%s%d' % (K, k), fill=(255, 255, 255))
    rows.append(row)
cw = max(r.width for r in rows)
out = Image.new('RGB', (3 * (cw + 10), 3 * (th + 40)), (30, 30, 30))
for i, r in enumerate(rows):
    out.paste(r, ((i % 3) * (cw + 10), (i // 3) * (th + 40)))
out.save(OUT + '/compare_c%s.png' % K)
log.close()
