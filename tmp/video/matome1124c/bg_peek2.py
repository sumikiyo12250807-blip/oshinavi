# -*- coding: utf-8 -*-
# 背景の動画 73197 を見る：0,4,8,12,16,19.5 秒のコマを並べ、上下の明るさを出す → bgpeek/all.png
import os, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import imageio_ffmpeg
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
os.makedirs(D + 'bgpeek', exist_ok=True)
ff = imageio_ffmpeg.get_ffmpeg_exe()
ims = []
for i, t in enumerate((0, 4, 8, 12, 16, 19.5)):
    p = D + 'bgpeek/b%d.png' % i
    subprocess.run([ff, '-y', '-v', 'error', '-ss', str(t), '-i', D + 'bg.mp4', '-frames:v', '1', p], capture_output=True)
    im = Image.open(p).convert('RGB')
    a = np.asarray(im).astype(float).mean(axis=2)
    print('%4.1f秒 全体 %.0f 上1/3 %.0f 中 %.0f 下1/3 %.0f' % (t, a.mean(), a[:120].mean(), a[120:240].mean(), a[240:].mean()))
    ims.append(im)
out = Image.new('RGB', (2 * 650, 3 * 370), (0, 0, 0))
for i, im in enumerate(ims):
    out.paste(im, ((i % 2) * 650, (i // 2) * 370))
out.save(D + 'bgpeek/all.png')
