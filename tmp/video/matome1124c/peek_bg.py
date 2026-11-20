# -*- coding: utf-8 -*-
import subprocess, imageio_ffmpeg
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-v', 'error', '-ss', '3', '-i', 'C:/Users/user/Downloads/91898_640x360.mp4', '-frames:v', '1', 'C:/Users/user/oshinavi/tmp/video/matome1124c/bg_peek0.png'])
