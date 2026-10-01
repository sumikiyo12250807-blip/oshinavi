# -*- coding: utf-8 -*-
# Mamma Mia 3本目 clip3.mp4（10.7MB）を10MB未満に縮める → clip3_x.mp4（2本目の clip2_x と同じ扱い）
import subprocess, os, imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
src = 'C:/Users/user/oshinavi/tmp/video/mamma/clip3.mp4'
dst = 'C:/Users/user/oshinavi/tmp/video/mamma/clip3_x.mp4'
p = subprocess.run([ff, '-y', '-i', src, '-c:v', 'libx264', '-b:v', '5500k', '-maxrate', '6000k', '-bufsize', '8000k',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', dst], capture_output=True)
print('exit', p.returncode, os.path.getsize(dst))
