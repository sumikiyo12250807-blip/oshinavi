# -*- coding: utf-8 -*-
# 全編のあと：長さ・大きさを測る → 書き出した動画から 12 コマ（終わり2秒前 65.6 秒を含む）を取り出して並べる（自分で見る）
#   → Downloads に oshinavi_1114_owarai_matome.mp4 / _x.mp4 を写す → finish14.txt・check14.png
import io, os, re, shutil, subprocess
from PIL import Image, ImageDraw
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
DL = 'C:/Users/user/Downloads/'
ff = imageio_ffmpeg.get_ffmpeg_exe()
out = []
for f in ('out.mp4', 'out_x.mp4'):
    r = subprocess.run([ff, '-i', D + f], capture_output=True, text=True, errors='replace').stderr
    out.append('%s %.2fMB %s' % (f, os.path.getsize(D + f) / 1048576, ' '.join(re.findall(r'Duration: [\d:.]+|\d{3,4}x\d{3,4}|[\d.]+ fps|Audio: \w+', r))))
TS = [2.5, 8.0, 12.0, 21.5, 30.0, 40.5, 45.0, 50.0, 54.0, 58.0, 62.0, 65.6]
g = Image.new('RGB', (6 * 270, 2 * 500), (0, 0, 0))
d = ImageDraw.Draw(g)
for i, t in enumerate(TS):
    p = D + 'chk_%04.1f.png' % t
    subprocess.run([ff, '-y', '-v', 'error', '-ss', str(t), '-i', D + 'out.mp4', '-frames:v', '1', p])
    im = Image.open(p).convert('RGB')
    if t == 65.6:
        im.save(D + 'end_full.png')
    g.paste(im.resize((270, 480)), ((i % 6) * 270, (i // 6) * 500 + 20))
    d.text(((i % 6) * 270 + 4, (i // 6) * 500 + 4), '%.1f' % t, fill=(255, 255, 0))
g.save(D + 'check14.png')
shutil.copyfile(D + 'out.mp4', DL + 'oshinavi_1114_owarai_matome.mp4')
shutil.copyfile(D + 'out_x.mp4', DL + 'oshinavi_1114_owarai_matome_x.mp4')
out.append('Downloads に写した')
io.open(D + 'finish14.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
