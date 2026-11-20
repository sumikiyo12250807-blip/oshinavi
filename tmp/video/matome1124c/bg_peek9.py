# -*- coding: utf-8 -*-
# 背景 7472（10秒）の 3 コマ（1・5・9 秒）を取り出して明るさを測る → bgpeek_*.png・bg_peek9.txt
import io, subprocess
import numpy as np
import imageio_ffmpeg
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
ff = imageio_ffmpeg.get_ffmpeg_exe()
out = io.open(D + 'bg_peek9.txt', 'w', encoding='utf-8')
ims = []
for i, t in enumerate((1, 5, 9)):
    p = D + 'bgpeek_%d.png' % i
    subprocess.run([ff, '-y', '-v', 'error', '-ss', str(t), '-i', D + 'bg_src.mp4', '-frames:v', '1', p])
    a = np.asarray(Image.open(p).convert('L')).astype(float)
    out.write('%ds 全体 %.0f 上1/3 %.0f 中 %.0f 下 %.0f\n' % (t, a.mean(), a[:120].mean(), a[120:240].mean(), a[240:].mean()))
    ims.append(Image.open(p))
g = Image.new('RGB', (640, 1080))
for i, im in enumerate(ims):
    g.paste(im, (0, 360 * i))
g.save(D + 'bgpeek_all.png')
out.close()
