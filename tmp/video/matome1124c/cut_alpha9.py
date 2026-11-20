# -*- coding: utf-8 -*-
# 11/4 第4版の切り抜き（すちこ「頭が切れてる」「衣装が消えてしまってる」）
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


R = [0, cut_at(FG.sum(axis=1), int(H * .27), int(H * .40)), cut_at(FG.sum(axis=1), int(H * .60), int(H * .73)), H]   # 11/14 1536×1024 のシート＝割合で探す
C = [0, cut_at(FG.sum(axis=0), int(W * .27), int(W * .40)), cut_at(FG.sum(axis=0), int(W * .60), int(W * .73)), W]
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
        flat = np.full((H, W, 3), 128, np.uint8)
        ws = cv2.watershed(flat, mk)
        for v in ks:
            OWN[comp & (ws == v)] = v
        edge = comp & (ws == -1)
        OWN[edge] = ks[0]
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
    ys, xs = np.where(al > 20)
    bb = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    out = rgba.copy()
    out[:, :, 3] = al
    Image.fromarray(out).crop(bb).save(D + 'poses/%s%d.png' % (PX, k))
    log.write('%s%d 大きさ %s シート上 (%d, %d, %d, %d)\n' % (PX, k, (bb[2] - bb[0], bb[3] - bb[1]), *bb))
log.close()
