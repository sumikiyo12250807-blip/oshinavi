# -*- coding: utf-8 -*-
# 舞台・トークショー 11/18 の全編（out_x.mp4・8.2MB）を Downloads へ（TikTok・X とも同じ1本）＋音と映像の長さ＋終わり2秒前の1コマ
import shutil, subprocess, re, io
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
DL = 'C:/Users/user/Downloads/'
shutil.copyfile(D + 'out_x.mp4', DL + 'oshinavi_1118_stage_matome.mp4')
e = subprocess.run([ff, '-i', D + 'out_x.mp4'], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
out = ['out_x.mp4 ' + ' '.join(re.findall(r'Duration: [\d:.]+|Stream #\S+ \S+ (?:Video|Audio): \w+[^,]*, [^,]*, \d+x\d+', e))]
subprocess.run([ff, '-y', '-v', 'error', '-sseof', '-2', '-i', D + 'out_x.mp4', '-frames:v', '1', D + 'end_full.png'])
io.open(D + 'to_dl.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
