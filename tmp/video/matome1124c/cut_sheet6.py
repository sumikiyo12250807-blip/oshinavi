# -*- coding: utf-8 -*-
# ドレス9着の切り抜き 第2版（cut_sheet4 は箱が隣の人のすそ・髪まで抜いた＝すそと次の人の頭が上下でくっついている）
#   ①1着ずつ広めの箱を isnet-anime で抜き（2倍）、シート全体の前景（市松模様を除く）に重ねる
#   ②1着ずつ「確実にその人」の芯（箱のまん中）を種にして、元の絵の色の境目で watershed＝すそと髪の境は色の境で分かれる
#   ③その人の分だけ残し、いちばん大きい塊＋中の穴埋め
#   → poses/p1〜p9.png・poses/compare.png・cut_sheet5.txt
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
S = 2
BOX = {1: (95, 0, 350, 452), 2: (510, 0, 810, 452), 3: (955, 15, 1265, 448),
       4: (85, 450, 370, 820), 5: (460, 462, 975, 805), 6: (1035, 438, 1250, 820),
       7: (50, 808, 395, 1195), 8: (455, 812, 945, 1195), 9: (970, 808, 1285, 1199)}
_a = np.asarray(sheet).astype(int)
_neu = (_a.max(axis=2) - _a.min(axis=2) < 7) & (_a.sum(axis=2) > 3 * 200)
_lum = _a.sum(axis=2) / 3
_A = _neu & (_lum >= 239)
_B = _neu & (_lum >= 210) & (_lum < 239)
_fa = cv2.blur(_A.astype(np.float32), (25, 25))
_fb = cv2.blur(_B.astype(np.float32), (25, 25))
CHK = (_fa > 0.2) & (_fb > 0.2) & (_fa + _fb > 0.85)
CHK = (cv2.dilate(CHK.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0) & _neu
big = sheet.resize((W * S, H * S), Image.LANCZOS)
CHK2 = cv2.resize(CHK.astype(np.uint8), big.size, interpolation=cv2.INTER_NEAREST) > 0
log = open(D + 'cut_sheet5.txt', 'w', encoding='utf-8')


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
ALPHA = np.where(CHK2, 0, ALPHA).astype(np.uint8)
FG = ALPHA > 60
mk = np.zeros(FG.shape, np.int32)
# 背景の種は置かない（置くと背景が髪の花飾りの弱い境から入り込んで食べた）＝人どうしだけで分け、あとで前景に絞る
# 下の段の人は頭（髪・花飾り）にも種を置く＝上の人のすその色と、花飾りの色の境で分かれる
#   上の段の人はすそ・靴にも種を置く（置かないと下の人の頭の種がすそ・靴まで流れ込んだ＝p7 に黒い靴・p8 にラベンダーのすそ）
#   箱はつなぎ目の拡大（poses/junction.png）で決めた。1人に複数の箱
HEAD = {6: [(1060, 445, 1200, 560)], 4: [(120, 458, 290, 580)], 7: [(150, 815, 310, 930)], 8: [(480, 818, 660, 960)], 9: [(1040, 815, 1195, 960)], 5: [(480, 470, 680, 620)]}
FOOT = {1: [(125, 405, 335, 440)], 2: [(530, 390, 770, 440)], 3: [(985, 400, 1255, 440)], 4: [(130, 770, 345, 812)], 5: [(815, 530, 965, 640)], 6: [(1045, 785, 1215, 815)]}
TOPCLIP = {}
_hsv = cv2.cvtColor(np.asarray(big), cv2.COLOR_RGB2HSV_FULL).astype(int)     # H 0〜255（=0〜360°）
HUE, SAT = _hsv[:, :, 0] * 360 // 256, _hsv[:, :, 1]
YY = np.arange(H * S)[:, None]
XX = np.arange(W * S)[None, :]
# 隣の人の色のかけら（view.png で見た）：p4 の足元に p7 のピンクの髪／p8 の頭の両脇に p5 のラベンダーのすそ／p9 の頭の上に p6 の赤いすそ・左上の灰色の線
DROP = {}
_NEU2 = cv2.resize(_neu.astype(np.uint8), big.size, interpolation=cv2.INTER_NEAREST) > 0
_LUM2 = cv2.resize(_lum.astype(np.float32), big.size, interpolation=cv2.INTER_NEAREST)
for k, v in FOOT.items():
    HEAD[k] = HEAD.get(k, []) + v
for k, (x0, y0, x1, y1) in BOX.items():
    w, h = x1 - x0, y1 - y0
    a, b, c, d = int((x0 + w * 0.22) * S), int((y0 + h * 0.22) * S), int((x1 - w * 0.22) * S), int((y1 - h * 0.22) * S)
    core = np.zeros(FG.shape, bool)
    core[b:d, a:c] = True
    for hx0, hy0, hx1, hy1 in HEAD.get(k, []):
        core[hy0 * S:hy1 * S, hx0 * S:hx1 * S] = True
    mk[core & FG] = k
img = cv2.cvtColor(np.asarray(big), cv2.COLOR_RGB2BGR)
lab_ws = cv2.watershed(img, mk.copy())
res = {}
for k, (x0, y0, x1, y1) in BOX.items():
    # シート全体の watershed は、遠くの人の種が背景を通って p3 の頭・花・グラスまで流れ込んだ
    #   ＝その人の箱の中だけで、箱の中にある種（本人＋となりの人のすそ・頭）どうしで分ける
    sub = mk[y0 * S:y1 * S, x0 * S:x1 * S].copy()
    lw = cv2.watershed(np.ascontiguousarray(img[y0 * S:y1 * S, x0 * S:x1 * S]), sub)
    mine = np.zeros(lab_ws.shape, bool)
    mine[y0 * S:y1 * S, x0 * S:x1 * S] = (lw == k)
    mine = cv2.dilate(mine.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0     # watershed の境目の1px（-1）を戻す
    km = np.where(mine, ALPHA, 0).astype(np.uint8)
    if k in TOPCLIP:
        km[:TOPCLIP[k] * S] = 0
    if k in DROP:
        km = np.where(DROP[k], 0, km).astype(np.uint8)
    # 細い線（透かしの線・境のかけら）でつながった遠くの破片を切る＝7px で開いて一番大きい塊だけ→少し広げて元と重ねる
    op = cv2.morphologyEx((km > 60).astype(np.uint8), cv2.MORPH_OPEN, np.ones((11, 11), np.uint8))
    n0, l0, s0, _ = cv2.connectedComponentsWithStats(op, 8)
    if n0 > 1:
        big0 = (l0 == 1 + int(np.argmax(s0[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
        km = np.where(cv2.dilate(big0, np.ones((11, 11), np.uint8)) > 0, km, 0).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats((km > 60).astype(np.uint8), 8)
    main = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    keep = [main] + [j for j in range(1, n) if j != main and st[j, cv2.CC_STAT_AREA] > st[main, cv2.CC_STAT_AREA] * 0.004
                     and st[main, 0] <= cen[j][0] <= st[main, 0] + st[main, 2] and st[main, 1] <= cen[j][1] <= st[main, 1] + st[main, 3]]
    km = np.where(np.isin(lab, keep), km, 0).astype(np.uint8)
    solid = (km > 60).astype(np.uint8)
    ff = np.pad(1 - solid, 1, constant_values=1).copy()
    fm = np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8)
    cv2.floodFill(ff, fm, (0, 0), 2)
    holes = (ff[1:-1, 1:-1] == 1) & ~CHK2
    km = np.where(holes, 255, km).astype(np.uint8)
    inner = cv2.erode((solid | holes).astype(np.uint8), np.ones((17, 17), np.uint8))
    km = np.maximum(km, np.where(CHK2, 0, inner * 255)).astype(np.uint8)
    # ふちに残った市松模様の白・灰のにじみ（暗い背景で白い縁に見える）を落とす。白いドレス（p7）は縁そのものが白なのでしない
    if k not in (3, 8):
        for _ in range(2):
            core_ = cv2.erode((km > 60).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
            ring = (km > 0) & ~core_
            km = np.where(ring & _NEU2 & (_LUM2 >= 205), 0, km).astype(np.uint8)
    ys, xs = np.where(km > 60)
    bb = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    rgba = big.convert('RGBA')
    rgba.putalpha(Image.fromarray(km))
    im = rgba.crop(bb)
    im.save(os.path.join(OUT, 'p%d.png' % k))
    res[k] = (im, tuple(v / S for v in bb))
    log.write('p%d 大きさ %s 塊 %d シート上 %s\n' % (k, im.size, len(keep), tuple(int(v) for v in res[k][1])))
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
