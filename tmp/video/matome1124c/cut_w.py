# -*- coding: utf-8 -*-
# 11/12 冬雪の子（cut_alpha9 の写し・切れ目の探す範囲だけ変えた）／元：11/4 第4版の切り抜き（すちこ「頭が切れてる」「衣装が消えてしまってる」）
#   シートはもともと透明の背景付き＝人の形は alpha のまま使う（isnet も色の watershed も使わない＝第3版は色の境目で髪の先・手を切った）
#   ①alpha>40 のつながった塊に分ける
#   ②塊の中に「人の芯（マスのまん中）」が1つだけ→丸ごとその人／2つ以上（隣とくっついている）→その塊の中だけ、形のくびれ（距離変換）で watershed
#   ③芯を含まない小さな塊（髪の毛先のかけら）→いちばん近い人の塊へ（距離 40px まで）
#   使い方: python cut_alpha9.py sheet_a.png a → poses/a1〜a9.png・cut9_a.txt
import io, os, sys
import numpy as np
import cv2
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
SH, PX = sys.argv[1], sys.argv[2]
src = Image.open(D + SH).convert('RGBA')
W, H = src.size
rgba = np.asarray(src).copy()
A = rgba[:, :, 3].astype(np.int32)
mx = max(1, int(np.percentile(A[A > 0], 99)))
A2 = np.clip(A * 255 // mx, 0, 255).astype(np.uint8)
FG = (A2 > 40).astype(np.uint8)
log = io.open(D + 'cut9_%s.txt' % PX, 'w', encoding='utf-8')


def cut_at(prof, lo, hi):
    seg = prof[lo:hi].astype(np.float32).reshape(-1, 1)
    return lo + int(np.argmin(cv2.blur(seg, (1, 9)).ravel()))


R = [0, cut_at(FG.sum(axis=1), 300, 420), cut_at(FG.sum(axis=1), 600, 720), H]
C = [0, cut_at(FG.sum(axis=0), 430, 560), cut_at(FG.sum(axis=0), 930, 1060), W]
log.write('行の切れ目 %s 列の切れ目 %s\n' % (R, C))
CORE = np.zeros((H, W), np.int32)
k = 0
for r in range(3):
    for c in range(3):
        k += 1
        x0, y0, x1, y1 = C[c], R[r], C[c + 1], R[r + 1]
        w, h = x1 - x0, y1 - y0
        CORE[int(y0 + h * 0.3):int(y1 - h * 0.3), int(x0 + w * 0.3):int(x1 - w * 0.3)] = k
n, lab, st, cen = cv2.connectedComponentsWithStats(FG, 8)
OWN = np.zeros((H, W), np.int32)
orphan = []
for j in range(1, n):
    comp = lab == j
    ks = [v for v in np.unique(CORE[comp]) if v and (comp & (CORE == v)).sum() > 200]
    if len(ks) == 1:
        OWN[comp] = ks[0]
    elif len(ks) >= 2:
        # くっついているのは細いつなぎ目（上の子のくつ／下の子の髪）＝塊を少しずつ細らせ、芯どうしが別の塊に離れた所で止める
        #   → 離れた芯の塊を種にして、元の塊の中だけで広げ直す（色の無い平らな絵で watershed＝近いほうへ）＝線でまっすぐ切らない（線より上に出た頭を残す）
        cm = comp.astype(np.uint8)
        seeds = None
        for e in range(1, 40):
            er = cv2.erode(cm, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * e + 1, 2 * e + 1)))
            m2, l2 = cv2.connectedComponents(er, 8)
            owner = {}
            ok = True
            for v in ks:
                vals, cnt = np.unique(l2[(CORE == v) & (er > 0)], return_counts=True)
                if not len(vals):
                    ok = False; break
                owner[v] = int(vals[np.argmax(cnt)])
            if ok and len(set(owner.values())) == len(ks):
                seeds = (l2, owner, e)
                break
        mk = np.zeros((H, W), np.int32)
        mk[~comp] = 99
        if seeds:
            l2, owner, e = seeds
            for v, lv in owner.items():
                mk[l2 == lv] = v
        else:
            for v in ks:
                mk[comp & (CORE == v)] = v
        lab_ = np.where(comp, np.where(mk == 99, 0, mk), 0).astype(np.int32)
        ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        for _it in range(2000):
            free = comp & (lab_ == 0)
            if not free.any():
                break
            ch = False
            for v in ks:
                g = (cv2.dilate((lab_ == v).astype(np.uint8), ker) > 0) & free
                if g.any():
                    lab_[g] = v; free &= ~g; ch = True
            if not ch:
                break
        for v in ks:
            OWN[comp & (lab_ == v)] = v
        log.write('  細らせた %s\n' % (seeds[2] if seeds else 'なし'))
        log.write('くっついた塊 %d 人 %s\n' % (j, ks))
    else:
        orphan.append(j)
for j in orphan:
    comp = (lab == j).astype(np.uint8)
    ring = cv2.dilate(comp, np.ones((81, 81), np.uint8)) > 0
    vs, cnt = np.unique(OWN[ring & (OWN > 0)], return_counts=True)
    if len(vs):
        OWN[comp > 0] = int(vs[np.argmax(cnt)])
# BANDFIX
BAND = np.zeros((H, W), bool)
for rr in R[1:3]:
    BAND[max(0, rr - 30):rr + 30] = True
for _ in range(3):
    for k in range(1, 10):
        mk_ = (OWN == k).astype(np.uint8)
        op = cv2.morphologyEx(mk_, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0
        thin = (mk_ > 0) & ~op & BAND
        if not thin.any():
            continue
        best = None
        for v in range(1, 10):
            if v == k:
                continue
            nv = cv2.dilate((OWN == v).astype(np.uint8), np.ones((13, 13), np.uint8)) > 0
            mv = thin & nv
            if mv.sum() > 5:
                OWN[mv] = v
                log.write('帯の細い所 %d → %d （%d 点）\n' % (k, v, int(mv.sum())))
# GIVEBACK：細い弧を持ち主へ返す
for _ in range(2):
    for k in range(1, 10):
        mk_ = ((OWN == k) & (FG > 0)).astype(np.uint8)
        op = cv2.morphologyEx(mk_, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
        n4, l4, s4, _c4 = cv2.connectedComponentsWithStats(op, 8)
        if n4 <= 1:
            continue
        body = l4 == 1 + int(np.argmax(s4[1:, cv2.CC_STAT_AREA]))
        keep = cv2.dilate(body.astype(np.uint8), np.ones((13, 13), np.uint8)) > 0
        rest = (OWN == k) & ~keep
        if not rest.any():
            continue
        n5, l5 = cv2.connectedComponents(rest.astype(np.uint8), 8)
        for j in range(1, n5):
            pc = l5 == j
            ring = cv2.dilate(pc.astype(np.uint8), np.ones((21, 21), np.uint8)) > 0
            vs, cnt = np.unique(OWN[ring & (OWN > 0) & (OWN != k)], return_counts=True)
            if len(vs) and cnt.max() > 30:
                OWN[pc] = int(vs[np.argmax(cnt)])
                log.write('返した %d → %d （%d 点）\n' % (k, int(vs[np.argmax(cnt)]), int(pc.sum())))
os.makedirs(D + 'poses', exist_ok=True)
for k in range(1, 10):
    mine = cv2.dilate((OWN == k).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0       # 縁の薄い alpha（40 以下）も本人のそばは残す
    # 本人のマスから上下 80・左右 60 より外は捨てる（遠くの子のかけら）＝そのあと本人のいちばん大きい塊＋そのそばの塊だけ
    r_, c_ = (k - 1) // 3, (k - 1) % 3
    box = np.zeros((H, W), bool)
    box[max(0, R[r_] - 80):min(H, R[r_ + 1] + 80), max(0, C[c_] - 60):min(W, C[c_ + 1] + 60)] = True
    mine &= box
    m3, l3, s3, c3 = cv2.connectedComponentsWithStats((mine & (A2 > 40)).astype(np.uint8), 8)
    if m3 > 1:
        big = 1 + int(np.argmax(s3[1:, cv2.CC_STAT_AREA]))
        near = cv2.dilate((l3 == big).astype(np.uint8), np.ones((41, 41), np.uint8)) > 0
        keepl = [j for j in range(1, m3) if j == big or (near & (l3 == j)).any()]
        mine &= cv2.dilate(np.isin(l3, keepl).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    others = cv2.dilate(((OWN > 0) & (OWN != k)).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    al = np.where(mine & ~((OWN != k) & (OWN > 0)), A2, 0).astype(np.uint8)
    # SPECK
    oth = cv2.dilate(((OWN > 0) & (OWN != k)).astype(np.uint8), np.ones((17, 17), np.uint8)) > 0
    n6, l6, s6, _c6 = cv2.connectedComponentsWithStats((al > 20).astype(np.uint8), 8)
    if n6 > 1:
        bigc = 1 + int(np.argmax(s6[1:, cv2.CC_STAT_AREA]))
        for j in range(1, n6):
            if j != bigc and s6[j, cv2.CC_STAT_AREA] < 600 and (oth & (l6 == j)).any():
                al[l6 == j] = 0
                log.write('  %s%d かけらを消した %d 点 (%d,%d)\n' % (PX, k, s6[j, cv2.CC_STAT_AREA], s6[j, 0], s6[j, 1]))
    ys, xs = np.where(al > 20)
    bb = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    out = rgba.copy()
    out[:, :, 3] = al
    Image.fromarray(out).crop(bb).save(D + 'poses/%s%d.png' % (PX, k))
    log.write('%s%d 大きさ %s シート上 (%d, %d, %d, %d)\n' % (PX, k, (bb[2] - bb[0], bb[3] - bb[1]), *bb))
log.close()
