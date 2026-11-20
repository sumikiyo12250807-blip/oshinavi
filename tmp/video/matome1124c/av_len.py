# -*- coding: utf-8 -*-
# out_x.mp4 の映像と音をそれぞれ最後まで読んで長さを出す・chk コマを1枚に並べる → art/chk.png
import glob, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
import imageio_ffmpeg
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
ff = imageio_ffmpeg.get_ffmpeg_exe()
for k, m in (('映像', '0:v'), ('音', '0:a')):
    e = subprocess.run([ff, '-i', D + 'out_x.mp4', '-map', m, '-f', 'null', '-'], capture_output=True, text=True, errors='replace').stderr
    print(k, re.findall(r'time=([\d:.]+)', e)[-1])
fs = sorted(glob.glob(D + 'frames/chk_*.png'))
o = Image.new('RGB', (len(fs) * 280, 480))
for i, f in enumerate(fs):
    o.paste(Image.open(f).convert('RGB'), (i * 280, 0))
o.save(D + 'art/chk.png')
print([f[-10:] for f in fs])
