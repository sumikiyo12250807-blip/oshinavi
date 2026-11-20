# -*- coding: utf-8 -*-
# 全編の締めの1コマ（終わりの2秒前 73.7 秒）→ final/end_73.7.png
import os, subprocess
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
os.makedirs(D + 'final', exist_ok=True)
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-v', 'error', '-ss', '73.7', '-i', D + 'out_x.mp4', '-frames:v', '1', D + 'final/end_73.7.png'], check=True)
print('ok')
