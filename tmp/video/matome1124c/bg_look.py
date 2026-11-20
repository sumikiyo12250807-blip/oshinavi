# -*- coding: utf-8 -*-
# 背景 141688 の長さと、0/25/50/75% の静止画を縦に切った形で4枚並べる → bg_look.png
import os, re, subprocess
import imageio_ffmpeg
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
ff = imageio_ffmpeg.get_ffmpeg_exe()
info = subprocess.run([ff, '-i', D + 'bg_src.mp4'], capture_output=True, text=True, errors='replace').stderr
m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', info)
dur = int(m.group(2)) * 60 + float(m.group(3))
print('dur', dur, [l.strip() for l in info.splitlines() if 'Video' in l])
ims = []
for k in range(4):
    t = dur * k / 4
    p = D + 'bgl_%d.png' % k
    subprocess.run([ff, '-y', '-v', 'error', '-ss', str(t), '-i', D + 'bg_src.mp4', '-frames:v', '1', '-vf', 'scale=-2:1920,crop=1080:1920', p])
    ims.append(Image.open(p).resize((270, 480)))
out = Image.new('RGB', (270 * 4 + 30, 480))
for k, im in enumerate(ims):
    out.paste(im, (k * 280, 0))
out.save(D + 'bg_look.png')
