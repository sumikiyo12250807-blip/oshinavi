# -*- coding: utf-8 -*-
import subprocess, io, re
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
src = 'C:/Users/user/Downloads/背景動画/96057_640x360.mp4'
D = 'C:/Users/user/oshinavi/tmp/x1123/songs/'
p = subprocess.run([ff, '-i', src], capture_output=True, text=True, encoding='utf-8', errors='replace')
io.open(D + 'bgframe.txt', 'w', encoding='utf-8').write('\n'.join(l for l in p.stderr.splitlines() if 'Duration' in l or 'Video:' in l))
for i, t in enumerate((1, 5, 10)):
    subprocess.run([ff, '-y', '-v', 'error', '-ss', str(t), '-i', src, '-frames:v', '1', D + 'bg96057_%d.png' % i])
subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'bg96057_0.png', '-i', D + 'bg96057_1.png', '-i', D + 'bg96057_2.png', '-filter_complex', 'hstack=inputs=3', D + 'bg96057_strip.png'])
