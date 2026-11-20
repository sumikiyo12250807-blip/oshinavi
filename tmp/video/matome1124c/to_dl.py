# -*- coding: utf-8 -*-
# J-POP 11/17 の全編を Downloads へ（TikTok 用＝大きい版・X 用＝_x）＋音と映像の長さ＋終わり2秒前の1コマ
import shutil, subprocess, re, io
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
DL = 'C:/Users/user/Downloads/'
shutil.copyfile(D + 'out.mp4', DL + 'oshinavi_1117_jpop_matome.mp4')
shutil.copyfile(D + 'out_x.mp4', DL + 'oshinavi_1117_jpop_matome_x.mp4')
out = []
for f in ('out.mp4', 'out_x.mp4'):
    e = subprocess.run([ff, '-i', D + f], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
    out.append(f + ' ' + ' '.join(re.findall(r'Duration: [\d:.]+|Stream #\S+ \S+ (?:Video|Audio): \w+', e)))
subprocess.run([ff, '-y', '-v', 'error', '-sseof', '-2', '-i', D + 'out.mp4', '-frames:v', '1', D + 'end_full.png'])
io.open(D + 'to_dl.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
