# -*- coding: utf-8 -*-
# 背景の雲を消す（10/30 すちこ「背景の雲☁️消して」）＝bgf/ の縦コマ450枚 → bgf_nc/
#   ①雲は動かない＝450枚の中央値の絵で、左の雲のない所（x0〜400）の行ごとの空の色を「その高さの空」とし、
#     それより明るい所（雲と光のにじみ）を雲の形にする（広げて、ふちをぼかす）
#   ②雲の所は、その高さの空の色（行ごと・左の空の中央値＝紺〜紫のグラデーション）で埋める
#   ③星を残す：同じコマの下のほう（y+760・x を 330 ずらす）の星の光だけを足す＝雲の所にもまたたく星が出る
#   → bgf_nc/%04d.jpg・bg_nocloud.png（1枚）・bg_nocloud_cmp.png（前後の比較）
import glob, os, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import cv2
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
fs = sorted(glob.glob(D + 'bgf/*.jpg'))
O = D + 'bgf_nc/'
os.makedirs(O, exist_ok=True)
sample = np.stack([np.asarray(Image.open(f).convert('RGB')).astype(np.float32) for f in fs[::15]])
med = np.median(sample, axis=0)
Hh, Ww = med.shape[:2]
sky = np.median(med[:, 0:400], axis=1)                     # 行ごとの空の色（雲のない左側）
sky = cv2.GaussianBlur(sky[:, None, :], (1, 41), 0)[:, 0, :]  # 縦になめらかに
diff = med.mean(axis=2) - sky.mean(axis=1)[:, None]
cloud = ((diff > 5) & (np.arange(Hh)[:, None] < 700)).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(cloud, 8)
keep = np.zeros_like(cloud)
for j in range(1, n):
    if st[j, cv2.CC_STAT_AREA] > 2000:                     # 星（小さな点）は雲にしない
        keep[lab == j] = 1
keep = cv2.dilate(keep, np.ones((41, 41), np.uint8))
alpha = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 18)[..., None]
alpha = np.clip(alpha * 1.3, 0, 1)
print('雲の所 %d px・範囲 y<%d' % (int(keep.sum()), int(np.where(keep.any(axis=1))[0].max())))
SKY = np.repeat(sky[:, None, :], Ww, axis=1)
DY, DX = 760, 330


def clean(a):
    src = np.roll(np.roll(a, -DY, axis=0), DX, axis=1)
    sky_src = np.roll(SKY, -DY, axis=0)
    stars = np.clip(src - sky_src - 6, 0, 255)               # 下の空の星の光だけ
    fill = SKY + stars
    return np.clip(a * (1 - alpha) + fill * alpha, 0, 255).astype(np.uint8)


for i, f in enumerate(fs):
    out = clean(np.asarray(Image.open(f).convert('RGB')).astype(np.float32))
    Image.fromarray(out).save(O + os.path.basename(f), quality=92)
    if i == 99:
        Image.fromarray(out).save(D + 'bg_nocloud.png')
        before = Image.open(f).convert('RGB').resize((540, 960))
        cmp_ = Image.new('RGB', (1100, 960), (40, 40, 40))
        cmp_.paste(before, (0, 0)); cmp_.paste(Image.fromarray(out).resize((540, 960)), (560, 0))
        cmp_.save(D + 'bg_nocloud_cmp.png')
print('frames', len(fs))
