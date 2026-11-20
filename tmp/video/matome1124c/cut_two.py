# -*- coding: utf-8 -*-
# 11/3：シート2枚（どちらも透明の地つき＝アルファあり）から 9 着ずつ切り抜く
#   ①アルファ≥128 の塊を種にする（3000px 未満のかけらは種にしない）
#   ②上下につながった塊（立ちの列・座りの右列）は、行の境の目安 ±70px の帯で「アルファの和が最小の横の縫い目」（1列で±1px まで曲がる）を探して切る
#      ＝靴と次の人の頭が光でつながっていても、すき間（いちばん薄い所）で分かれる
#   ③アルファ>0 の画素は、いちばん近い種の人に入れる（髪の端・光のふち・離れた小物）
#   ④ふちの色の光（アルファの薄い所）は 48 未満を消す
#   ⑤外接矩形が切った縫い目・シートの端に触れたら「欠けの印」を出す
#   → poses/a1〜a9.png（座り）・b1〜b9.png（立ち）・poses/compare_a.png・compare_b.png・cut_two.txt
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np, cv2
from scipy import ndimage
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
OUT = D + 'poses/'
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    os.remove(OUT + f)
log = open(D + 'cut_two.txt', 'w', encoding='utf-8')
ROWB = {'a': [425, 840], 'b': [426, 850]}   # 行の境の目安（投影の谷）


def seam(alpha, x0, x1, ylo, yhi):
    """x0〜x1 の列を左から右へ、ylo〜yhi の帯の中で通るアルファ最小の横の縫い目（各列の y）"""
    a_ = alpha[ylo:yhi, x0:x1].astype(np.float64)
    cost = a_ + np.where(a_ >= 128, 2000.0, 0.0)     # 濃い所（体）を横切るのは高くつく＝薄い光のすき間を通る
    h, w = cost.shape
    acc = cost.copy()
    back = np.zeros((h, w), np.int64)
    for x in range(1, w):
        prev = acc[:, x - 1]
        cand = np.stack([np.r_[np.inf, prev[:-1]], prev, np.r_[prev[1:], np.inf]])
        k = cand.argmin(axis=0)
        acc[:, x] += cand[k, np.arange(h)]
        back[:, x] = np.arange(h) + k - 1
    ys = np.zeros(w, np.int64)
    ys[-1] = int(acc[:, -1].argmin())
    for x in range(w - 1, 0, -1):
        ys[x - 1] = back[ys[x], x]
    return ys + ylo, float(acc[ys[-1], -1])


def cut(tag):
    im = np.asarray(Image.open(D + 'sheet_%s.png' % tag).convert('RGBA')).copy()
    A = im[:, :, 3].astype(np.int32)
    H, W = A.shape
    m = (A >= 128).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
    seeds = np.zeros((H, W), np.int32)
    cuts = []
    nid = 0
    for j in range(1, n):
        if st[j, 4] < 3000:
            continue
        x, y, w, h = st[j, :4]
        reg = (lab == j)
        nk = int(round(h / 425.0)) - 1      # 1人の高さ ≒ 425 → 上下につながった人数 −1 本の縫い目
        ks = sorted(ROWB[tag], key=lambda b: abs(b - (y + h / 2)))[:nk] if nk > 0 else []
        ks = sorted(b for b in ks if y + 60 < b < y + h - 60)
        if not ks:
            nid += 1
            seeds[reg] = nid
            continue
        ycut = []
        for b in ks:
            aa = np.where(reg | ((A > 0) & (np.abs(np.arange(W)[None, :] - (x + w / 2)) < w / 2 + 5)), A, 0)
            ys, c = seam(aa, x, x + w, b - 25, b + 25)   # 帯を広げると細い脚を横切った（b5）＝靴底と頭の境の近くだけで探す
            ycut.append(ys)
            cuts.append((x, ys))
            log.write('%s 縫い目 x%d〜%d y%d〜%d アルファ和 %.0f\n' % (tag, x, x + w, ys.min(), ys.max(), c))
        yy = np.arange(H)[:, None]
        band = np.zeros((H, W), np.int64)
        for ys in ycut:
            col = np.zeros(W, np.int64) + 10 ** 6
            col[x:x + w] = ys
            band += (yy > col[None, :])
        for k in range(len(ks) + 1):
            part = reg & (band == k)
            if part.sum() > 3000:
                nid += 1
                seeds[part] = nid
    # ③ アルファ>0 の残りをいちばん近い種へ（縫い目をまたがないように、縫い目の線は種なし・通れる）
    dist, (iy, ix) = ndimage.distance_transform_edt(seeds == 0, return_indices=True)
    owner = np.where(dist <= 40, seeds[iy, ix], 0)     # 種から 40px より遠い薄い画素は誰のものにもしない
    # 縫い目をまたいだ持ち主は外す：縫い目の列の範囲で、縫い目の上の画素が下の人（またはその逆）になっていたら 0
    yy = np.arange(H)[:, None]
    for x, ys in cuts:
        col = np.full(W, -1, np.int64)
        col[x:x + len(ys)] = ys
        inr = col[None, :] >= 0
        below = yy > col[None, :]
        for k in range(1, nid + 1):
            sk = seeds == k
            sx = np.where(sk)[1].mean()
            if not (x <= sx < x + len(ys)):
                continue
            kb = below[sk & inr].mean() > 0.5 if (sk & inr).any() else None
            if kb is None:
                continue
            bad = (owner == k) & inr & (below != kb)
            owner[bad] = 0
    ids = sorted(range(1, nid + 1), key=lambda k: (int(np.mean(np.where(seeds == k)[0]) // 380), np.mean(np.where(seeds == k)[1])))
    res = []
    for r, k in enumerate(ids, 1):
        a = np.where((owner == k) & (A >= 48), A, 0).astype(np.uint8)
        ys, xs = np.where(a > 0)
        bb = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        touch = []
        if bb[0] <= 0 or bb[1] <= 0 or bb[2] >= W or bb[3] >= H:
            touch.append('シートの端')
        for x, sy in cuts:
            cols = np.arange(x, x + len(sy))
            on = (a[np.clip(sy, 0, H - 1), cols] > 0).sum() + (a[np.clip(sy - 1, 0, H - 1), cols] > 0).sum()
            if on > 0:
                hv = a[np.clip(sy, 0, H - 1), cols] > 0
                touch.append('縫い目に %d px（%s）' % (on, 'x%d〜%d' % (cols[hv].min(), cols[hv].max()) if hv.any() else ''))
        rgba = im.copy()
        rgba[:, :, 3] = a
        pi = Image.fromarray(rgba).crop(bb)
        name = '%s%d' % (tag, r)
        pi.save(OUT + name + '.png')
        res.append((name, pi, bb))
        log.write('%s 大きさ %s シート上 %s %s\n' % (name, pi.size, tuple(int(v) for v in bb), ' / '.join(touch) or '欠けの印なし'))
    # 元シートと並べる（左＝元・右＝切り抜きを灰色の地に）
    th = 420
    tiles = []
    sheet = Image.fromarray(im)
    for name, pi, bb in res:
        b = (max(0, bb[0] - 25), max(0, bb[1] - 25), min(W, bb[2] + 25), min(H, bb[3] + 25))
        o = Image.new('RGBA', (b[2] - b[0], b[3] - b[1]), (255, 255, 255, 255))
        sc = sheet.crop(b)
        o.paste(sc, (0, 0), sc)
        o = o.convert('RGB')
        o = o.resize((max(1, int(o.width * th / o.height)), th), Image.LANCZOS)
        g = Image.new('RGB', (int(pi.width * th / pi.height) + 30, th + 30), (70, 70, 80))
        r2 = pi.resize((int(pi.width * th / pi.height), th), Image.LANCZOS)
        g.paste(r2, (15, 15), r2)
        g = g.resize((int(g.width * th / g.height), th))
        row = Image.new('RGB', (o.width + g.width + 20, th + 30), (20, 20, 20))
        row.paste(o, (0, 30)); row.paste(g, (o.width + 20, 30))
        ImageDraw.Draw(row).text((4, 4), name, fill=(255, 255, 0))
        tiles.append(row)
    cw = max(t.width for t in tiles)
    out = Image.new('RGB', (3 * (cw + 10), 3 * (th + 40)), (20, 20, 20))
    for i, t in enumerate(tiles):
        out.paste(t, ((i % 3) * (cw + 10), (i // 3) * (th + 40)))
    out.save(OUT + 'compare_%s.png' % tag)


cut('a')
cut('b')
log.close()
print(open(D + 'cut_two.txt', encoding='utf-8').read())
