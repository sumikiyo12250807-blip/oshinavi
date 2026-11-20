# -*- coding: utf-8 -*-
# つなぎ目（44.521 秒）のまわりのコマを、出来上がり・つないだだけの映像・raw2 の頭から並べる（ブロックのにじみがどこで出たか）
import subprocess
from PIL import Image
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
DL = 'C:/Users/user/Downloads/oshinavi_1119_classic_matome.mp4'
shots = []
for nm, src, t in (('out44.4', DL, 44.4), ('out44.6', DL, 44.6), ('out45.5', DL, 45.5), ('out47', DL, 47.0),
                   ('joined44.6', D + 'joined.mp4', 44.6), ('raw2_0.1', D + 'raw2.mp4', 0.1), ('raw2_1.0', D + 'raw2.mp4', 1.0), ('raw1_end', D + 'raw1.mp4', 44.3)):
    p = D + 'pj_%s.png' % nm
    subprocess.run([ff, '-y', '-v', 'error', '-i', src, '-ss', str(t), '-frames:v', '1', p])
    shots.append(Image.open(p).convert('RGB').resize((270, 480)))
o = Image.new('RGB', (270 * 4, 480 * 2))
for i, s in enumerate(shots):
    o.paste(s, ((i % 4) * 270, (i // 4) * 480))
o.save(D + 'peek_join.png')
