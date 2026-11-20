# -*- coding: utf-8 -*-
import subprocess
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff, '-y', '-v', 'error', '-ss', '5', '-i', 'C:/Users/user/Downloads/背景動画/30729_640x360.mp4', '-frames:v', '1', 'C:/Users/user/oshinavi/tmp/video/matome1124c/src_peek.png'])
