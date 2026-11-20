# -*- coding: utf-8 -*-
# 切り抜きに残った市松模様のかけらを消して（p1 の足の間・足元／p4 の足元／p7 の頭の上の線）→ 本番を書き出す
import os, subprocess, sys
import numpy as np
from PIL import Image
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
P = D + 'poses/'
RECT = {'p1': [(.44, .66, .78, 1.0), (0, .965, 1, 1.0)], 'p4': [(.30, .93, .62, 1.0)]}
for n, rs in RECT.items():
    im = np.array(Image.open(P + n + '.png').convert('RGBA'))
    h, w = im.shape[:2]
    rgb = im[:, :, :3].astype(int)
    neu = (rgb.max(axis=2) - rgb.min(axis=2) < 16) & (rgb.sum(axis=2) >= 3 * 185)
    for a, b, c, d in rs:
        m = np.zeros((h, w), bool)
        m[int(b * h):int(d * h), int(a * w):int(c * w)] = True
        im[:, :, 3][m & neu] = 0
    Image.fromarray(im).save(P + n + '.png')
im = np.array(Image.open(P + 'p7.png').convert('RGBA'))
h, w = im.shape[:2]
im[:int(.012 * h), int(.55 * w):, 3] = 0
Image.fromarray(im).save(P + 'p7.png')
subprocess.run([sys.executable, D + 'zoom_p.py'])
env = dict(os.environ, PYTHONIOENCODING='utf-8')
r = subprocess.run([sys.executable, D + 'render.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
open(D + 'render_run.txt', 'w', encoding='utf-8').write('rc %s\n%s\n%s\n' % (r.returncode, r.stdout[-800:], r.stderr[-1500:]))
