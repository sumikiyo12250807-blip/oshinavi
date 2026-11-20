# -*- coding: utf-8 -*-
# 11/5 レインボー原宿アイドル九変化（1254x1254 RGBA・3x3）を9人に切る
#  ①行・列の切れ目＝alpha の濃い画素がいちばん少ない所（中央付近の範囲で探す）
#  ②1人ずつ、切れ目より少し広い箱を黒の上に置いて isnet-anime（1024）で抜く → 元の alpha と掛ける
#  ③いちばん大きい塊（＋中にある小さな塊）だけ残す。箱の端に触れたら「欠けの印」
#  → poses/a1〜a9.png・poses/compare.png・cut9.txt
import os, io, sys
import numpy as np
import cv2
import onnxruntime as ort
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
OUT = D + 'poses'
os.makedirs(OUT, exist_ok=True)
src = Image.open(D + 'sheet_a.png').convert('RGBA')
W, H = src.size
A = np.asarray(src)[:, :, 3].astype(int)
log = io.open(D + 'cut9.txt', 'w', encoding='utf-8')


def cut_at(prof, lo, hi):
    seg = prof[lo:hi]
    return lo + int(np.argmin(cv2.blur(seg.astype(np.float32).reshape(-1, 1), (1, 9)).ravel()))


rowp = (A > 90).sum(axis=1)
colp = (A > 90).sum(axis=0)
R = [0, cut_at(rowp, 340, 470), cut_at(rowp, 740, 860), H]
C = [0, cut_at(colp, 360, 470), cut_at(colp, 780, 880), W]
log.write('行の切れ目 %s 列の切れ目 %s\n' % (R, C))
sess = ort.InferenceSession('C:/Users/user/oshinavi/tmp/video/models/isnet-anime.onnx', providers=['CPUExecutionProvider'])
inp = sess.get_inputs()[0].name
black = Image.new('RGBA', src.size, (0, 0, 0, 255))
flat = Image.alpha_composite(black, src).convert('RGB')


def mask_of(c):
    x = np.asarray(c.resize((1024, 1024), Image.LANCZOS)).astype(np.float32)
    x = x / max(x.max(), 1e-6)
    x = (x - np.array([0.485, 0.456, 0.406], dtype=np.float32))
    x = x.transpose(2, 0, 1)[None].astype(np.float32)
    p = sess.run(None, {inp: x})[0][:, 0]
    p = (p - p.min()) / max(p.max() - p.min(), 1e-6)
    return np.asarray(Image.fromarray((p[0] * 255).astype(np.uint8)).resize(c.size, Image.LANCZOS)).astype(int)


PAD = 14
FILL = {3: (832, 230, 1078, 437)}   # zoom_a3.png：下のブーツは x915〜1070・y335〜437、その下は a6 の青い髪
CLIPBOT = {3: 437}
res = {}
k = 0
for r in range(3):
    for c in range(3):
        k += 1
        x0, y0 = max(0, C[c] - PAD), max(0, R[r] - PAD)
        x1, y1 = min(W, C[c + 1] + PAD), min(H, R[r + 1] + PAD)
        m = mask_of(flat.crop((x0, y0, x1, y1)))
        a = A[y0:y1, x0:x1]
        # 元の alpha は全体に薄い（a4・a5 が透けた）＝人の形は isnet の m だけで決め、元の alpha が無い所（<8）だけ落とす
        al = np.where((m < 50) | (a < 8), 0, np.clip((m - 50) * 3, 0, 255)).astype(np.uint8)   # isnet が迷って半端な濃さ（a4・a5）＝強めに上げる
        if k in FILL:   # isnet が落とした脚（a3 の左下のもこもこ）＝元の alpha の濃い所で、箱の指定範囲だけ足す
            fx0, fy0, fx1, fy1 = FILL[k]
            add = np.zeros(al.shape, bool)
            add[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0] = True
            al = np.where(add & (a > 60), np.maximum(al, np.clip(a * 1.5, 0, 255)), al).astype(np.uint8)
        if k in CLIPBOT:
            al[CLIPBOT[k] - y0:] = 0
        n, lab, st, cen = cv2.connectedComponentsWithStats((al > 60).astype(np.uint8), 8)
        main = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        keep = [main] + [j for j in range(1, n) if j != main and st[j, cv2.CC_STAT_AREA] > st[main, cv2.CC_STAT_AREA] * 0.003
                         and st[main, 0] <= cen[j][0] <= st[main, 0] + st[main, 2] and st[main, 1] <= cen[j][1] <= st[main, 1] + st[main, 3]]
        if k in FILL:   # 足した範囲にかかる塊は残す（a3 の下のブーツは本体の箱の外に中心がある）
            fx0, fy0, fx1, fy1 = FILL[k]
            keep += [j for j in range(1, n) if j not in keep and st[j, cv2.CC_STAT_AREA] > 300
                     and (lab[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0] == j).any()]
        al = np.where(np.isin(lab, keep), al, 0).astype(np.uint8)
        ys, xs = np.where(al > 60)
        bb = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        edge = [s for s, v in (('左', bb[0] <= 1 and x0 > 0), ('上', bb[1] <= 1 and y0 > 0), ('右', bb[2] >= al.shape[1] - 1 and x1 < W), ('下', bb[3] >= al.shape[0] - 1 and y1 < H)) if v]
        piece = src.crop((x0, y0, x1, y1)).copy()
        piece.putalpha(Image.fromarray(al))
        im = piece.crop(bb)
        im.save(os.path.join(OUT, 'a%d.png' % k))
        res[k] = (im, (x0 + bb[0], y0 + bb[1], x0 + bb[2], y0 + bb[3]))
        log.write('a%d 大きさ %s 塊 %d シート上 %s 端に触れた %s\n' % (k, im.size, len(keep), res[k][1], ''.join(edge) or 'なし'))
th = 420
rows = []
for k in range(1, 10):
    im, box = res[k]
    b = (max(0, box[0] - 20), max(0, box[1] - 20), min(W, box[2] + 20), min(H, box[3] + 20))
    o = flat.crop(b)
    o = o.resize((int(o.width * th / o.height), th), Image.LANCZOS)
    g = Image.new('RGB', (int(im.width * th / im.height) + 40, th + 40), (0, 150, 60))
    r2 = im.resize((int(im.width * th / im.height), th), Image.LANCZOS)
    g.paste(r2, (20, 20), r2)
    g = g.resize((int(g.width * th / g.height), th))
    row = Image.new('RGB', (o.width + g.width + 30, th + 30), (30, 30, 30))
    row.paste(o, (0, 30)); row.paste(g, (o.width + 30, 30))
    ImageDraw.Draw(row).text((4, 4), 'a%d' % k, fill=(255, 255, 255))
    rows.append(row)
cw = max(r.width for r in rows)
out = Image.new('RGB', (3 * (cw + 10), 3 * (th + 40)), (30, 30, 30))
for i, r in enumerate(rows):
    out.paste(r, ((i % 3) * (cw + 10), (i // 3) * (th + 40)))
out.save(OUT + '/compare.png')
log.close()
