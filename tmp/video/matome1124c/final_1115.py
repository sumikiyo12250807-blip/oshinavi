# -*- coding: utf-8 -*-
# 書き出し後の点検：out_full／out_x の映像と音の長さ・大きさ、終わりの2秒前のコマ（end2.png）→ Downloads へ写す → final_1115.txt
import io, os, re, shutil, subprocess
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
ff = imageio_ffmpeg.get_ffmpeg_exe()
out = []


def lens(p):
    r = subprocess.run([ff, '-v', 'error', '-i', p, '-map', '0:v', '-f', 'null', '-'], capture_output=True, text=True, errors='replace')
    info = subprocess.run([ff, '-i', p], capture_output=True, text=True, errors='replace').stderr
    dur = re.search(r'Duration: ([\d:.]+)', info).group(1)
    # 映像と音の長さを別々に測る（それぞれの流れだけを数える）
    res = {}
    for kind, mp in (('映像', '0:v'), ('音', '0:a')):
        q = subprocess.run([ff, '-v', 'quiet', '-stats', '-i', p, '-map', mp, '-f', 'null', '-'], capture_output=True, text=True, errors='replace').stderr
        t = re.findall(r'time=(\d+):(\d+):([\d.]+)', q)
        h, m, s = t[-1]
        res[kind] = int(h) * 3600 + int(m) * 60 + float(s)
    return dur, res


for f in ('out_full.mp4', 'out_x.mp4'):
    p = D + f
    dur, res = lens(p)
    out.append('%s 大きさ %.2fMB 長さ %s 映像 %.2f秒 音 %.2f秒 差 %.2f秒' % (f, os.path.getsize(p) / 1048576, dur, res['映像'], res['音'], res['映像'] - res['音']))
t2 = 109.3 - 2.0
subprocess.run([ff, '-y', '-v', 'error', '-ss', '%.2f' % t2, '-i', D + 'out_full.mp4', '-frames:v', '1', D + 'end2.png'])
from PIL import Image
Image.open(D + 'end2.png').resize((540, 960)).save(D + 'end2_s.png')
DL = 'C:/Users/user/Downloads/'
shutil.copyfile(D + 'out_full.mp4', DL + 'oshinavi_1115_owarai_matome.mp4')
out.append('写した %s %.2fMB' % (DL + 'oshinavi_1115_owarai_matome.mp4', os.path.getsize(DL + 'oshinavi_1115_owarai_matome.mp4') / 1048576))
if os.path.getsize(D + 'out_full.mp4') > 10 * 1048576:
    shutil.copyfile(D + 'out_x.mp4', DL + 'oshinavi_1115_owarai_matome_x.mp4')
    out.append('10MB を超えた＝X 用 %s %.2fMB' % (DL + 'oshinavi_1115_owarai_matome_x.mp4', os.path.getsize(DL + 'oshinavi_1115_owarai_matome_x.mp4') / 1048576))
io.open(D + 'final_1115.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
