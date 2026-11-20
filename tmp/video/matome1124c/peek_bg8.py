# -*- coding: utf-8 -*-
# 背景 97396 の情報と3コマ・曲の長さ
import io, re, subprocess
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
ff = imageio_ffmpeg.get_ffmpeg_exe()
o = []
for f in ('bg_src.mp4', 'song.mp3'):
    r = subprocess.run([ff, '-i', D + f], capture_output=True, text=True, errors='replace').stderr
    o.append(f + ' ' + ' '.join(re.findall(r'Duration: [\d:.]+|\d+(?:\.\d+)? fps|\d{3,4}x\d{3,4}', r)))
for i, t in enumerate((1, 5, 9)):
    subprocess.run([ff, '-y', '-v', 'error', '-ss', str(t), '-i', D + 'bg_src.mp4', '-frames:v', '1', D + 'bgpeek_%d.png' % i])
io.open(D + 'peek_bg8.txt', 'w', encoding='utf-8').write('\n'.join(o))
