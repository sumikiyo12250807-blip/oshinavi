# -*- coding: utf-8 -*-
# oshimade_full.mp4（23MB・約69秒）をXに上げられる10MB未満に縮める → oshimade_full_x.mp4
import subprocess, os, imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
src = 'C:/Users/user/oshinavi/tmp/video/oshimade/oshimade_full.mp4'
dst = 'C:/Users/user/oshinavi/tmp/video/oshimade/oshimade_full_x.mp4'
cmd = [ff, '-y', '-i', src, '-vf', 'scale=720:-2', '-c:v', 'libx264', '-b:v', '950k', '-maxrate', '1100k', '-bufsize', '2000k',
       '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', dst]
p = subprocess.run(cmd, capture_output=True)
print('exit', p.returncode, os.path.getsize(dst) if os.path.exists(dst) else 0)
print(p.stderr.decode('utf-8', 'replace')[-400:])
