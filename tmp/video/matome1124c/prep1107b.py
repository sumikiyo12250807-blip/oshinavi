# -*- coding: utf-8 -*-
# 11/7：k2 の下の髪のかけら（k5 の髪の線）を落とす・拍（138BPM 付近をスネアで）・背景ループ長 9.1 秒
import io, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
import numpy as np, cv2
from PIL import Image
out = io.open(D + 'prep1107b.txt', 'w', encoding='utf-8')
im = Image.open(D + 'poses/k2.png').convert('RGBA')
a = np.asarray(im).copy()
m = (a[:, :, 3] > 20).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
near = cv2.dilate((lab == big).astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
keep = np.zeros_like(m, bool)
for j in range(1, n):
    if j == big or (st[j, cv2.CC_STAT_AREA] > 300 and (near & (lab == j)).any()):
        keep |= lab == j
keep = cv2.dilate(keep.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
a[:, :, 3] = np.where(keep, a[:, :, 3], 0)
ys, xs = np.where(a[:, :, 3] > 20)
Image.fromarray(a).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(D + 'poses/k2.png')
out.write('k2 塊 %d → 大きさ %s\n' % (n - 1, (xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)))
# k5 は頭のてっぺんが k2 の足とくっついて欠けた＝使わない（poses から外す）
if os.path.exists(D + 'poses/k5.png'):
    os.replace(D + 'poses/k5.png', D + 'k5_unused.png')
s = io.open(D + 'beats_snare.py', encoding='utf-8').read()
s = s.replace('END = 65.8', 'END = 139.3').replace('np.arange(98.5, 101.51, 0.02)', 'np.arange(137.0, 139.01, 0.02)')
io.open(D + 'beats_snare.py', 'w', encoding='utf-8').write(s)
s = io.open(D + 'bg_video.py', encoding='utf-8').read()
s = s.replace('FPS, L, XF = 30.0, 9.95, 0.6', 'FPS, L, XF = 30.0, 9.05, 0.6')
io.open(D + 'bg_video.py', 'w', encoding='utf-8').write(s)
s = io.open(D + 'beat_char.py', encoding='utf-8').read()
s = s.replace("poses/e[1-9].png'))   # 11/6 バレエコア e1〜e9", "poses/k[1-9].png'))   # 11/7 着物の歌姫 k")
io.open(D + 'beat_char.py', 'w', encoding='utf-8').write(s)
r = subprocess.run([sys.executable, D + 'beats_snare.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
out.write('beats rc %s %s\n' % (r.returncode, r.stderr[-1500:]))
out.write(io.open(D + 'beats_snare.txt', encoding='utf-8').read())
out.close()
