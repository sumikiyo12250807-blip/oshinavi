# -*- coding: utf-8 -*-
# 書き出したX用の動画から6コマ抜いて1枚に並べる（最後の確認）
import subprocess, sys, os
import imageio_ffmpeg
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/' + sys.argv[1] + '/'
src = D + sys.argv[2]
ts = [float(x) for x in sys.argv[3].split(',')]
ff = imageio_ffmpeg.get_ffmpeg_exe()
ims = []
for i, t in enumerate(ts):
    p = D + 'peek_%d.png' % i
    subprocess.run([ff, '-y', '-v', 'error', '-ss', str(t), '-i', src, '-frames:v', '1', '-vf', 'scale=270:480', p])
    ims.append(Image.open(p))
W = Image.new('RGB', (275 * len(ims), 480), (20, 20, 20))
for i, im in enumerate(ims):
    W.paste(im, (i * 275, 0))
W.save(D + 'final_peek.png')
