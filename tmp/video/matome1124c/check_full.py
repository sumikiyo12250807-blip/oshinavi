# -*- coding: utf-8 -*-
# 書き出した全編から12コマ取り出して並べる（衣装の順・字・締めの5人を見る）→ check_full.png・Downloads へ写す
import os, shutil, subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
ff = imageio_ffmpeg.get_ffmpeg_exe()
T = [5.0, 13.0, 17.0, 20.2, 23.0, 28.0, 35.0, 41.0, 47.0, 51.5, 61.0, 73.6]
w, h = 270, 480
out = Image.new('RGB', (6 * (w + 6), 2 * (h + 30)), (30, 30, 30))
for i, t in enumerate(T):
    p = D + 'chk_%04.1f.png' % t
    subprocess.run([ff, '-y', '-v', 'error', '-ss', str(t), '-i', D + 'out.mp4', '-frames:v', '1', p], check=True)
    im = Image.open(p).convert('RGB').resize((w, h))
    x, y = (i % 6) * (w + 6), (i // 6) * (h + 30)
    out.paste(im, (x, y + 26))
    ImageDraw.Draw(out).text((x + 4, y + 4), '%.1f' % t, fill=(255, 255, 255))
out.save(D + 'check_full.png')
shutil.copyfile(D + 'out.mp4', 'C:/Users/user/Downloads/oshinavi_1116_sports_matome.mp4')
shutil.copyfile(D + 'out_x.mp4', 'C:/Users/user/Downloads/oshinavi_1116_sports_matome_x.mp4')
print('ok')
