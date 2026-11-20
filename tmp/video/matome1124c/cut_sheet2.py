# -*- coding: utf-8 -*-
# きらめきフェアリーの切り抜きを作り直す（2026-10-26 すちこ「妖精の足が欠けてる…元画像はちゃんと欠けてないから切り方が悪い」）
#   第1版は 3 等分の格子で切った＝足や靴がとなりのコマにはみ出した分が落ちた
#   ①コマの真ん中（3 等分の格子の中心）を軸に、上下左右へ 22% ずつ広げた範囲を切り出し、2 倍にして isnet-anime で抜く
#   ②つながった塊のうち、コマの中心に一番近い大きな塊（＝そのコマの妖精）と、それにほぼ接する塊（羽の薄い所で切れた分）だけ残す
#     となりのコマの絵ははなれた塊なので落ちる。小さい蝶・キラキラ（本体の 4% 未満）も落ちる
#   ③残した塊の外接矩形が切り出し範囲の端に触れていたら（＝欠けの印）範囲を広げてやり直す
#   → poses/p1〜p9.png（上書き）・比較画像 poses/compare.png（左＝元のシートの同じ所・右＝切り抜き・緑の地）
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
log = open(D + 'cut_sheet2.txt', 'w', encoding='utf-8')


def mask_of(c):
    x = np.asarray(c.resize((1024, 1024), Image.LANCZOS)).astype(np.float32)
    x = x / max(x.max(), 1e-6)
    x = (x - np.array([0.485, 0.456, 0.406], dtype=np.float32)) / np.array([1.0, 1.0, 1.0], dtype=np.float32)
    x = x.transpose(2, 0, 1)[None].astype(np.float32)
    p = sess.run(None, {inp: x})[0][:, 0]
    p = (p - p.min()) / max(p.max() - p.min(), 1e-6)
    return Image.fromarray((p[0] * 255).astype(np.uint8)).resize(c.size, Image.LANCZOS)


def cut(k, pad):
    r, c = (k - 1) // 3, (k - 1) % 3
    cw, chh = W / 3, H / 3
    x0, x1 = max(0, int(cw * c - cw * pad)), min(W, int(cw * (c + 1) + cw * pad))
    y0, y1 = max(0, int(chh * r - chh * pad)), min(H, int(chh * (r + 1) + chh * pad))
    reg = sheet.crop((x0, y0, x1, y1))
    S = 2
    big = reg.resize((reg.width * S, reg.height * S), Image.LANCZOS)
    m = np.asarray(mask_of(big))
    m = np.where(m < 40, 0, np.where(m > 200, 255, m)).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats((m > 60).astype(np.uint8), 8)
    # コマの中心（切り出し範囲の中の座標）
    ccx, ccy = (cw * (c + 0.5) - x0) * S, (chh * (r + 0.5) - y0) * S
    cands = [j for j in range(1, n) if st[j, cv2.CC_STAT_AREA] > (cw * chh * S * S) * 0.05]
    main = min(cands, key=lambda j: (cen[j][0] - ccx) ** 2 + (cen[j][1] - ccy) ** 2)
    keep = {main}
    mb = st[main]
    # 本体の外接矩形を少し広げた中に重心がある中くらいの塊（羽の切れ端・杖の先）も残す
    ex = 0.06 * max(mb[2], mb[3])
    for j in range(1, n):
        if j == main or st[j, cv2.CC_STAT_AREA] < st[main, cv2.CC_STAT_AREA] * 0.04:
            continue
        cx, cy = cen[j]
        if mb[0] - ex <= cx <= mb[0] + mb[2] + ex and mb[1] - ex <= cy <= mb[1] + mb[3] + ex:
            keep.add(j)
    km = np.where(np.isin(lab, list(keep)), m, 0).astype(np.uint8)
    ys, xs = np.where(km > 60)
    bb = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    edge = bb[0] <= 2 or bb[1] <= 2 or bb[2] >= big.width - 2 or bb[3] >= big.height - 2
    # シートの外枠に触れているのは欠けではない（元の絵の端）
    real_edge = (bb[0] <= 2 and x0 > 0) or (bb[1] <= 2 and y0 > 0) or (bb[2] >= big.width - 2 and x1 < W) or (bb[3] >= big.height - 2 and y1 < H)
    rgba = big.convert('RGBA')
    rgba.putalpha(Image.fromarray(km))
    return rgba.crop(bb), real_edge, (x0, y0, x1, y1), [(x0 + bb[0] / S), (y0 + bb[1] / S), (x0 + bb[2] / S), (y0 + bb[3] / S)], len(keep)


res = {}
for k in range(1, 10):
    for pad in (0.22, 0.32, 0.45):
        im, e, reg, box, nk = cut(k, pad)
        log.write('p%d pad %.2f 範囲 %s 絵 %s 塊 %d 端に触れる %s\n' % (k, pad, reg, [round(v) for v in box], nk, e))
        if not e:
            break
    im.save(os.path.join(OUT, 'p%d.png' % k))
    res[k] = (im, box)
    log.write('p%d -> %s\n' % (k, im.size))
# 比較画像：左＝元のシートの同じ所（絵の外接矩形＋余白 20px）・右＝切り抜き（緑の地）
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
cols = 3
cw = max(r.width for r in rows)
out = Image.new('RGB', (cols * (cw + 10), 3 * (th + 40)), (30, 30, 30))
for i, r in enumerate(rows):
    out.paste(r, ((i % cols) * (cw + 10), (i // cols) * (th + 40)))
out.save(OUT + '/compare.png')
log.close()
print('ok')
