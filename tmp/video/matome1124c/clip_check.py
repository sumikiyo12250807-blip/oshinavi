# -*- coding: utf-8 -*-
# 試し動画の長さ・音の有無と、衣装が替わる前後のコマ（拍の沈み込み・入れ替えを見る）
import json, io, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
import imageio_ffmpeg
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
ff = imageio_ffmpeg.get_ffmpeg_exe()
r = subprocess.run([ff, '-i', D + 'clip.mp4'], capture_output=True, text=True, encoding='utf-8', errors='replace')
print('\n'.join(l.strip() for l in r.stderr.splitlines() if 'Duration' in l or 'Stream' in l))
S = json.load(io.open(D + 'stage_1118_v.json', encoding='utf-8'))
print('poses', S['poses'][:3])
ch = S['poses'][1][0]
ims = []
for t in (1.0, ch - 0.2, ch + 0.2, 9.5):
    subprocess.run([ff, '-y', '-v', 'error', '-ss', '%.2f' % t, '-i', D + 'clip.mp4', '-frames:v', '1', D + 'frames/c_%.2f.png' % t])
    ims.append(Image.open(D + 'frames/c_%.2f.png' % t).resize((270, 480)))
out = Image.new('RGB', (4 * 280, 480), (30, 30, 30))
for i, im in enumerate(ims):
    out.paste(im, (i * 280, 0))
out.save(D + 'frames/clip_check.png')
