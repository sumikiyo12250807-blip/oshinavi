# -*- coding: utf-8 -*-
# 11/16 姐さんのスポーツ9人（sports_chibi_1116.png・1536x1024・RGB＝ぼかしの背景が描き込み）を9人に切る
#  ①行・列の切れ目＝背景との差（彩度と明るさの変化）がいちばん少ない帯を探す
#  ②1人ずつ、切れ目より広い箱で isnet-anime（1024）にかけて抜く
#  ③大きい塊（本体）と、本体の 0.4% より大きい塊（ボール・ポンポン・ペンライトなど体から離れた小物）を残す。箱の端に触れたら欠けの印
#  → poses/w1〜w9.png（右向き＝シートのまま）・m1〜m9（反転）・look_all.png・cut_sports.txt
import os, io
import numpy as np
import cv2
import onnxruntime as ort
from PIL import Image, ImageDraw, ImageOps
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
OUT = D + 'poses'
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    if f.endswith('.png'):
        os.remove(os.path.join(OUT, f))
src = Image.open(D + 'sheet.png').convert('RGB')
W, H = src.size
arr = np.asarray(src).astype(np.float32)
# 背景はやわらかいぼかし＝縦横の微分が小さい。人のいる所は線が多い＝勾配の強さで切れ目を探す
g = np.abs(np.diff(arr.mean(axis=2), axis=0))[:, :-1] + np.abs(np.diff(arr.mean(axis=2), axis=1))[:-1, :]
edge = (g > 18).astype(np.float32)
rowp, colp = edge.sum(axis=1), edge.sum(axis=0)


def cut_at(prof, lo, hi):
    seg = cv2.blur(prof[lo:hi].reshape(-1, 1), (1, 15)).ravel()
    return lo + int(np.argmin(seg))


R = [0, cut_at(rowp, 290, 380), cut_at(rowp, 630, 720), H]
C = [0, cut_at(colp, 440, 560), cut_at(colp, 960, 1060), W]
log = io.open(D + 'cut_sports.txt', 'w', encoding='utf-8')
log.write('行の切れ目 %s 列の切れ目 %s\n' % (R, C))
sess = ort.InferenceSession('C:/Users/user/oshinavi/tmp/video/models/isnet-anime.onnx', providers=['CPUExecutionProvider'])
inp = sess.get_inputs()[0].name


def mask_of(c):
    x = np.asarray(c.resize((1024, 1024), Image.LANCZOS)).astype(np.float32)
    x = x / max(x.max(), 1e-6)
    x = (x - np.array([0.485, 0.456, 0.406], dtype=np.float32))
    x = x.transpose(2, 0, 1)[None].astype(np.float32)
    p = sess.run(None, {inp: x})[0][:, 0]
    p = (p - p.min()) / max(p.max() - p.min(), 1e-6)
    return np.asarray(Image.fromarray((p[0] * 255).astype(np.uint8)).resize(c.size, Image.LANCZOS)).astype(int)


PAD = 10
res = {}
k = 0
for r in range(3):
    for c in range(3):
        k += 1
        x0, y0 = max(0, C[c] - PAD), max(0, R[r] - PAD)
        x1, y1 = min(W, C[c + 1] + PAD), min(H, R[r + 1] + PAD)
        crop = src.crop((x0, y0, x1, y1))
        m = mask_of(crop)
        al = np.clip((m - 40) * 2.2, 0, 255).astype(np.uint8)
        n, lab, st, cen = cv2.connectedComponentsWithStats((al > 60).astype(np.uint8), 8)
        main = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        hh, ww = al.shape
        # 小物（ボール・ペンライト）は残す／上下の段の子の髪や足のかけら（箱の上か下の端に触れる塊）は落とす
        keep = [main] + [j for j in range(1, n) if j != main and st[j, cv2.CC_STAT_AREA] > st[main, cv2.CC_STAT_AREA] * 0.004
                         and st[j, cv2.CC_STAT_TOP] > 2 and st[j, cv2.CC_STAT_TOP] + st[j, cv2.CC_STAT_HEIGHT] < hh - 2]
        al = np.where(np.isin(lab, keep), al, 0).astype(np.uint8)
        ys, xs = np.where(al > 60)
        bb = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        edg = [s for s, v in (('左', bb[0] <= 1 and x0 > 0), ('上', bb[1] <= 1 and y0 > 0), ('右', bb[2] >= al.shape[1] - 1 and x1 < W), ('下', bb[3] >= al.shape[0] - 1 and y1 < H)) if v]
        piece = crop.convert('RGBA')
        piece.putalpha(Image.fromarray(al))
        im = piece.crop(bb)
        im.save(os.path.join(OUT, 'w%d.png' % k))
        ImageOps.mirror(im).save(os.path.join(OUT, 'm%d.png' % k))
        res[k] = (im, (x0 + bb[0], y0 + bb[1], x0 + bb[2], y0 + bb[3]))
        log.write('w%d 大きさ %s 塊 %d シート上 %s 端に触れた %s\n' % (k, im.size, len(keep), res[k][1], ''.join(edg) or 'なし'))
# 1人ずつ、元の絵と切り抜き（緑の地）を高さ 700 で横に並べる＝頭・髪の先・小物の欠けを見る
for k in range(1, 10):
    im, box = res[k]
    b = (max(0, box[0] - 25), max(0, box[1] - 25), min(W, box[2] + 25), min(H, box[3] + 25))
    o = src.crop(b)
    th = 700
    o = o.resize((int(o.width * th / o.height), th), Image.LANCZOS)
    g2 = Image.new('RGB', (o.width, th), (0, 150, 60))
    r2 = im.resize((int(im.width * th / (box[3] - box[1] + 50)), int(im.height * th / (box[3] - box[1] + 50))), Image.LANCZOS)
    g2.paste(r2, (int(25 * th / (box[3] - box[1] + 50)), int(25 * th / (box[3] - box[1] + 50))), r2)
    row = Image.new('RGB', (o.width * 2 + 20, th), (30, 30, 30))
    row.paste(o, (0, 0)); row.paste(g2, (o.width + 20, 0))
    ImageDraw.Draw(row).text((6, 6), 'w%d' % k, fill=(0, 0, 0))
    row.save(D + 'look_w%d.png' % k)
log.close()
